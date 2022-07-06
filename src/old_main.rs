use rand::prelude::*;
use serde::Deserialize;
use std::collections::{HashMap, HashSet};
use std::{env, fmt, fs};

use serenity::{
    async_trait,
    model::{channel::Message, gateway::Ready, id::UserId},
    prelude::*,
};

#[derive(Debug, PartialEq, Eq, Hash)]
enum Stage {
    Created,
    Nominate,
    TeamVote,
    Questing,
    LastStand,
    GameOver,
}

impl fmt::Display for Stage {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match *self {
            Stage::Created => writeln!(f, "Created"),
            Stage::Nominate => writeln!(f, "Nominate"),
            Stage::TeamVote => writeln!(f, "Team Vote"),
            Stage::Questing => writeln!(f, "Questing"),
            Stage::LastStand => writeln!(f, "Last Stand"),
            Stage::GameOver => writeln!(f, "Game Over"),
        }
    }  
}

#[derive(Debug, PartialEq, Eq, Hash)]
enum Vote {
    Yea,
    Nay,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
enum Role {
    EvilGuy = -5,
    EvilLancelot,
    Assassin,
    Morgana,
    Mordred,
    Oberon,
    GoodGuy,
    Merlin,
    Percival,
    GoodLancelot,
}

impl Default for Role {
    fn default() -> Self { Role::GoodGuy }
}

#[derive(Default, Deserialize, Debug)]
struct GameConfig {
    good_count: i32,
    evil_count: i32,
    quester_count: [usize; 5],
    double_fail: bool,
}

impl fmt::Display for GameConfig {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        writeln!(f, 
            "good_count: {}, evil_count: {}, quester_count: {:?}, double_fail: {}",
            self.good_count,
            self.evil_count,
            self.quester_count,
            self.double_fail)
    }
}

struct GameSession {
    host: UserId,
    config: GameConfig,
    players: Vec<UserId>,
    roles: Vec<Role>,
    stage: Stage,

    turn_index: usize,
    lady_index: i32,

    quests_passed: i32,
    quests_failed: i32,
    current_quest: usize,
    doom_counter: i32,
    questers: HashSet<UserId>,
    votes: HashMap<UserId, Vote>,

    merlins_watch_list: HashSet<UserId>,
    percival_watch_list: HashSet<UserId>,
    evil_watch_list: HashSet<UserId>,
    special_roles: HashMap<Role, bool>,
}

impl GameSession {
    fn next_stage(&mut self) -> Result<String, String> {
        match self.stage {
            Stage::Created => {
                if !self.player_count_check() {
                    // TODO: add Discord message saying lack of players
                    println!("Too few players!");
                    return Err(String::from("Attempted to start game with too few players!"));
                }
                // Get game configuration
                let data = fs::read_to_string("./settings.json").expect("Unable to open file");
                let mut config_map: HashMap<usize, GameConfig> = serde_json::from_str(data.as_str()).unwrap();
                let config = config_map.remove(&self.players.len());
                match config {
                    Some(valid_conf) => self.config = valid_conf,
                    None => return Err(String::from("Configuration loaded is malformed or not valid. Please redownload the settings.json file.")),
                }

                // Assign roles 
                let (mut special_evil_count, mut special_good_count) = (0, 0); //self.count_evil(&self.special_roles);
                for (role, val) in &self.special_roles {
                    if *val {
                        let role_num = *role as i32;
                        if role_num <= 0 {
                            special_evil_count += 1;
                        } else {
                            special_good_count += 1;
                        }
                    }
                }
                if special_evil_count > self.config.evil_count {
                    // TODO: Send message instead of printing
                    println!("Too many special evil roles!");
                    return Err(String::from("Attempted to start game with too many special evil roles"));
                }
                // Don't need to check special good roles, since it's impossible
                // to have more special good roles than the total number of good roles
                self.roles = vec![Role::Merlin, Role::Assassin];
                for (role, val) in &self.special_roles {
                    if *val {
                        self.roles.push(*role);
                    }
                }
                for _ in special_good_count + 1..self.config.good_count {
                    self.roles.push(Role::GoodGuy);
                }
                for _ in special_evil_count + 1..self.config.evil_count {
                    self.roles.push(Role::EvilGuy);
                }
                // self.include_roles(&mut self.special_evil, self.config.evil_count, Role::EvilGuy);
                // self.include_roles(&mut self.special_good, self.config.good_count, Role::GoodGuy);

                self.players.shuffle(&mut thread_rng());
                self.roles.shuffle(&mut thread_rng());
                for i in 0..self.roles.len() {
                    let role = self.roles[i];
                    let role_num = role as i32;
                    if role_num.abs() == 2 {
                        self.percival_watch_list.insert(self.players[i]);
                    }
                    if role_num < 0 {
                        if role_num < -1 {
                            self.merlins_watch_list.insert(self.players[i]);
                        }
                        self.evil_watch_list.insert(self.players[i]);
                    }
                }
                println!("{:?}", self.players);
                println!("{:?}", self.roles);
                println!("{:?}", self.percival_watch_list);
                println!("{:?}", self.merlins_watch_list);
                println!("{:?}", self.evil_watch_list);

                // send out DMs 
                // TODO: Once DM feature is done, add call here

                // randomly select king
                self.turn_index = thread_rng().gen_range(0..self.players.len());

                // change stage to nominate
                self.stage = Stage::Nominate;
            },
            Stage::Nominate => {
                if self.questers.len() != self.config.quester_count[self.current_quest] {
                    return Err(String::from("Can't continue to team voting without correct number of questers."));
                }
                // change state to TeamVote
                self.stage = Stage::TeamVote;
            },
            Stage::TeamVote => {
                for player in &self.players {
                    if !self.votes.contains_key(player) {
                        return Err(String::from("Not all players have voted yet!"));
                    }
                }

                // Result will be positive if majority vote for team
                let result: i32 = self.votes.values().map(|x| match *x {
                    Vote::Yea => 1,
                    Vote::Nay => -1,
                }).sum();

                // change state to Nominate or Game Over if votes fails, questing otherwise
                if result > 0 {
                    self.stage = Stage::Questing;
                } else {
                    self.doom_counter += 1;
                    self.stage = if self.doom_counter == 5 { Stage::GameOver } else {Stage::Nominate };
                }
                
                self.increment_turn();
                // Clear votes, so the map can be reused for next stage
                self.votes.clear();
            },
            Stage::Questing => {
                for player in &self.questers{
                    if !self.votes.contains_key(player) {
                        return Err(String::from("Not all questers have voted yet!"));
                    }
                }

                let result: usize = self.votes.values().map(|x| match *x {
                    Vote::Nay => 1,
                    _ => 0,
                }).sum();

                let df_adjust = if self.config.double_fail { 1 } else { 0 };

                let passed = result <= 0 + df_adjust;

                if passed {
                    self.quests_passed += 1;
                } else {
                    self.quests_failed += 1;
                }

                // change state to Nominate, LastStand, or GameOver accordingly
                if self.quests_passed == 3 {
                    self.stage = Stage::LastStand;
                } else if self.quests_failed == 3 {
                    self.stage = Stage::GameOver;
                } else {
                    self.stage = Stage::Nominate;
                }
            },
            Stage::LastStand => {
                // Not really much to do here???
                // change state to GameOver
                self.stage = Stage::GameOver
            },
            Stage::GameOver => {
                // I dunno what to do here honestly lmao
            }
        }

        // TODO: Change this message and use it for logging in the future.
        Ok(format!("Progressed to the {} stage", self.stage))
    }

    fn start_game(&mut self, id: UserId) -> Result<(), String> {
        if !self.player_count_check() {
            // TODO: add Discord message saying lack of players
            println!("Too few players!");
            return Err(String::from("Attempted to start game with too few players!"));
        }
        // Get game configuration
        let data = fs::read_to_string("./settings.json").expect("Unable to open file");
        let mut config_map: HashMap<usize, GameConfig> = serde_json::from_str(data.as_str()).unwrap();
        let config = config_map.remove(&self.players.len());
        match config {
            Some(valid_conf) => self.config = valid_conf,
            None => return Err(String::from("Configuration loaded is malformed or not valid. Please redownload the settings.json file.")),
        }

        // Assign roles 
        let (mut special_evil_count, mut special_good_count) = (0, 0); //self.count_evil(&self.special_roles);
        for (role, val) in &self.special_roles {
            if *val {
                let role_num = *role as i32;
                if role_num <= 0 {
                    special_evil_count += 1;
                } else {
                    special_good_count += 1;
                }
            }
        }
        if special_evil_count > self.config.evil_count {
            // TODO: Send message instead of printing
            println!("Too many special evil roles!");
            return Err(String::from("Attempted to start game with too many special evil roles"));
        }
        // Don't need to check special good roles, since it's impossible
        // to have more special good roles than the total number of good roles
        self.roles = vec![Role::Merlin, Role::Assassin];
        for (role, val) in &self.special_roles {
            if *val {
                self.roles.push(*role);
            }
        }
        for _ in special_good_count + 1..self.config.good_count {
            self.roles.push(Role::GoodGuy);
        }
        for _ in special_evil_count + 1..self.config.evil_count {
            self.roles.push(Role::EvilGuy);
        }
        // self.include_roles(&mut self.special_evil, self.config.evil_count, Role::EvilGuy);
        // self.include_roles(&mut self.special_good, self.config.good_count, Role::GoodGuy);

        self.players.shuffle(&mut thread_rng());
        self.roles.shuffle(&mut thread_rng());
        for i in 0..self.roles.len() {
            let role = self.roles[i];
            let role_num = role as i32;
            if role_num.abs() == 2 {
                self.percival_watch_list.insert(self.players[i]);
            }
            if role_num < 0 {
                if role_num < -1 {
                    self.merlins_watch_list.insert(self.players[i]);
                }
                self.evil_watch_list.insert(self.players[i]);
            }
        }
        println!("{:?}", self.players);
        println!("{:?}", self.roles);
        println!("{:?}", self.percival_watch_list);
        println!("{:?}", self.merlins_watch_list);
        println!("{:?}", self.evil_watch_list);

        // send out DMs 
        // TODO: Once DM feature is done, add call here

        // randomly select king
        self.turn_index = thread_rng().gen_range(0..self.players.len());

        // change stage to nominate
        self.stage = Stage::Nominate; 
        Ok(())
    }

    fn add_player(&mut self, id: UserId) -> Result<(), String> {
        if self.stage != Stage::Created {
            return Err(String::from("Attempted to add player to game that is already in progress!"));
        } else if self.players.contains(&id) {
            return Err(String::from("Attemped to add player to game that is already in the game!"));
        }
        self.players.push(id);

        Ok(())
    }

    fn player_count_check(&self) -> bool {
        let num_players = self.players.len();

        num_players >= 5 && num_players <= 10
    }

    fn increment_turn(&mut self) {
        self.turn_index = (self.turn_index + 1) % self.players.len();
    }

    fn nominate_players(&mut self, ids: Vec<UserId>) -> Result<(), String> {
        if self.stage != Stage::Nominate {
            return Err(String::from("Attempted to nominate player to quest when not in nominate stage!"));
        }
        if self.questers.len() + ids.len() > self.config.quester_count[self.current_quest] {
            return Err(String::from("Attempted to add too many players to the quest!"));
        }
        for id in ids {
            self.questers.insert(id);
        }
        Ok(())
    }

    fn vote(&mut self, id: UserId, vote: bool) -> Result<(), String> {
        if self.votes.contains_key(&id) {
            return Err(String::from("User has already voted!"));
        }

        let player_vote: Vote = if vote { Vote::Yea } else { Vote::Nay };

        self.votes.insert(id, player_vote);

        Ok(())
    }

    fn check_kill(self, id: UserId) -> bool {
        let mut iter = self.players.iter();
        let player_index = iter.position(|&x| x == id).unwrap();
        let player_role = self.roles[player_index];
        return player_role == Role::Merlin;
    }

}

fn build_session(host: UserId) -> GameSession {
    GameSession {
        host,
        config: GameConfig::default(),
        players: Vec::new(),
        roles: Vec::new(),
        stage: Stage::Created,
        turn_index: 0,
        lady_index: 0,
        quests_passed: 0,
        quests_failed: 0,
        current_quest: 0,
        doom_counter: 0,
        questers: HashSet::new(),
        votes: HashMap::new(),
        merlins_watch_list: HashSet::new(),
        percival_watch_list: HashSet::new(),
        evil_watch_list: HashSet::new(),
        special_roles: HashMap::from([
            (Role::Percival, false),
            (Role::GoodLancelot, false),
            (Role::Morgana, false),
            (Role::Mordred, false),
            (Role::Oberon, false),
            (Role::EvilLancelot, false),
        ]),
    }
}

const HELP_MESSAGE: &str = "Tough luck lmao";

const HELP_COMMAND: &str = "!help";

struct Handler;

#[async_trait]
impl EventHandler for Handler {
    async fn message(&self, ctx: Context, msg: Message) {
        if msg.content == HELP_COMMAND {
            if let Err(why) = msg.channel_id.say(&ctx.http, HELP_MESSAGE).await {
                println!("Error sending message: {:?}", why);
            }
        }
    }

    async fn ready(&self, _: Context, ready: Ready) {
        println!("{} is connected!", ready.user.name);
    }
}

#[tokio::main]
async fn main() {
    // !!! Remove once done with testing 
    /***********************************/
    let mut game_state: GameSession = build_session(UserId(69));
    for i in 0..10 {
        game_state.add_player(UserId(i));
    }
    // TODO: Use this Result for logging and/or stopping the game without crashing the bot
    game_state.next_stage();
    /***********************************/

    // let token = env::var("DISCORD_TOKEN")
    //     .expect("Expected a token in the environment");

    // let mut client = Client::builder(token)
    //     .event_handler(Handler)
    //     .await
    //     .expect("Err creating client");

    // if let Err(why) = client.start().await {
    //     println!("Client error: {:?}", why);
    // }
}