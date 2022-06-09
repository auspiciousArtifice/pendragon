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

// #[derive(Clone, Copy, Debug, Default, PartialEq, Eq, Hash)]
// struct Player {
//     id: UserId,
//     role: Role,
// }

#[derive(Default, Deserialize, Debug)]
struct GameConfig {
    good_count: i32,
    evil_count: i32,
    quester_count: [i32; 5],
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

struct GameState {
    config: GameConfig,
    players: Vec<UserId>,
    roles: Vec<Role>,
    stage: Stage,

    turn: i32,
    lady_index: i32,

    quests_passed: i32,
    quests_failed: i32,
    current_quest: i32,
    doom_counter: i32,
    questers: HashSet<UserId>,
    voted: HashSet<UserId>,

    merlins_watch_list: HashSet<UserId>,
    percival_watch_list: HashSet<UserId>,
    evil_watch_list: HashSet<UserId>,
    special_roles: HashMap<Role, bool>,
}

impl GameState {
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
                let mut special_evil_count = 0; //self.count_evil(&self.special_roles);
                let mut special_good_count = 0;
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
                self.turn = thread_rng().gen_range(0..self.players.len()) as i32;

                // change stage to nominate
                self.stage = Stage::Nominate;
            },
            Stage::Nominate => {

                // change state to TeamVote
                self.stage = Stage::TeamVote;
            },
            Stage::TeamVote => {

                // change state to Nominate if votes fails, questing otherwise
                
            },
            Stage::Questing => {

                // change state to Nominate, LastStand, or GameOver accordingly
            },
            Stage::LastStand => {

                // change state to GameOver
            },
            Stage::GameOver => {
                
                // I dunno what to do here honestly lmao
            }
        }

        // TODO: Change this message and use it for logging in the future.
        Ok(format!("Progressed to the {} stage", self.stage))
    }

    fn add_player(&mut self, id: UserId) -> Result<(), String> {
        if self.stage != Stage::Created {
            return Err(String::from("Attempted to add player to game that is already in progress!"));
        }
        self.players.push(id);

        Ok(())
    }

    fn player_count_check(&self) -> bool {
        self.players.len() >= 5
    }

    fn count_roles(&self, role_map: &HashMap<Role, bool>) -> i32 {
        let mut count = 0;
        for i in role_map.values() {
            count += if *i { 1 } else { 0 };
        }
        count
    }

    // fn include_roles(&mut self, 
    //                 role_map: &mut HashMap<Role, bool>, 
    //                 total_count: i32,
    //                 default_role: Role) {
    //     let mut count = 1;
    //     for role in role_map.keys() {
    //         if *role_map.get(role).unwrap() {
    //             self.roles.push(*role);
    //             count += 1;
    //         }
    //     }
    //     for _ in count..total_count {
    //         self.roles.push(default_role);
    //     }
    // }

    fn nominate_player(&self, id: UserId) {

    }
}

struct GameSession {
    host: UserId,
    involved_users: Vec<UserId>,
    state: GameState,
}

// fn build_player(id: UserId, role: Role) -> Player {
//     Player {
//         id,
//         role,
//     }
// }

fn build_game() -> GameState {
    GameState {
        config: GameConfig::default(),
        players: Vec::new(),
        roles: Vec::new(),
        stage: Stage::Created,
        turn: 0,
        lady_index: 0,
        quests_passed: 0,
        quests_failed: 0,
        current_quest: 0,
        doom_counter: 0,
        questers: HashSet::new(),
        voted: HashSet::new(),
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

fn build_session(host: UserId) -> GameSession {
    GameSession {
        host,
        involved_users: Vec::new(),
        state: build_game(),
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
    let mut game_state: GameState = build_game();
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