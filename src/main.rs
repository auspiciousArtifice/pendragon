use rand::prelude::*;
use serde::Deserialize;
use std::collections::{HashMap, HashSet};
use std::ops::Index;
use std::{env, fmt, fs};

use serenity::{
    async_trait,
    model::{channel::Message, gateway::Ready, id::UserId},
    prelude::*,
};

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
    good_count: usize,
    evil_count: usize,
    quester_count: [usize; 5],
    double_fail: bool,
}

#[derive(Debug, PartialEq, Eq, Hash)]
enum Vote {
    Yea,
    Nay,
}

struct AvalonFSM<S> {
    host: UserId,
    players: Vec<UserId>,
    roles: Vec<Role>,
    config: GameConfig,

    turn_index: usize,
    lady_index: usize,

    quests_passed: usize,
    quests_failed: usize,
    current_quest: usize,

    state: S,
}
impl AvalonFSM<Created> {
    fn new(host: UserId) -> Self {
        AvalonFSM {
            host,
            players: Vec::new(),
            roles: Vec::new(),
            config: GameConfig::default(),
            turn_index: 0,
            lady_index: 0,
            quests_passed: 0,
            quests_failed: 0,
            current_quest: 0,
            state: Created::new(),
        }
    }
}
struct Created {
    tentative_players: Vec<UserId>,
    special_roles: HashSet<Role>,
}
impl Created {
    fn new() -> Self {
        Created {
            tentative_players: Vec::new(),
            special_roles: HashSet::new(),
        }
    }

    fn add_player(&mut self, id: UserId) -> Result<UserId, String> {
        if self.tentative_players.contains(&id) {
            return Err(String::from("Attempted to add player to game that is already added!"));
        }

        self.tentative_players.push(id);
        Ok(id)
    }
    
    fn remove_player(&mut self, id: UserId) -> Result<UserId, String> {
        match self.tentative_players.iter().position(|&x| x == id) {
            Some(index) => {
                return Ok(self.tentative_players.remove(index));
            },
            None => {
                return Err(String::from("Attempted to remove player from game thtat wasn't added!"));
            },
        }
    }

    fn player_count_check(&self) -> bool {
        let num_players = self.tentative_players.len();
        num_players >= 5 && num_players <= 10
    }

    fn add_role(&mut self, role: Role) -> Result<Role, String> {
        if self.special_roles.contains(&role) {
            return Err(String::from(format!("{:?} has already been added to the game!", role)));
        }

        self.special_roles.insert(role);
        Ok(role)
    }

    fn remove_role(&mut self, role: Role) -> Result<Role, String> {
        match self.special_roles.take(&role) {
            Some(removed_role) => {
                return Ok(removed_role);
            },
            None => {
                return Err(String::from(format!("{:?} has not been added to the game yet!", role)));
            },
        }
    }
}

struct Nominate {
    doom_counter: usize,
    nominated_players: HashSet<UserId>,
}
impl Nominate {
    fn new(doom_counter: usize) -> Self {
        Nominate {
            doom_counter,
            nominated_players: HashSet::new(),
        }
    }
}
impl TryFrom<AvalonFSM<Created>> for AvalonFSM<Nominate> {
    type Error = (); // TODO: Change the error type to something more appropriate
    fn try_from(val: AvalonFSM<Created>) -> Result<AvalonFSM<Nominate>, Self::Error> {
        // TODO: Add logic for assigning random roles, turn, lady, etc.
        if val.players.len() < 5 ||val.players.len() > 10 {
            return Err(()); // TODO: Add some error message or some way to compare
        }

        let data = fs::read_to_string("./settings.json").expect("Unable to open file");
        let mut config_map: HashMap<usize, GameConfig> = serde_json::from_str(data.as_str()).unwrap();
        let config: GameConfig = config_map.remove(&val.players.len()).expect("Config file is malformed or not valid");

        // Assign roles
        let (mut evil_roles, mut good_roles) = (0, 0);
        for role in &val.state.special_roles {
            let role_num = *role as i32;
            if role_num <= 0 {
                evil_roles += 1;
            } else {
                good_roles += 1;
            }
        }
        if evil_roles > config.evil_count {
            // TODO: Send message instead of printing
            println!("Too many special evil roles!");
            return Err(()); // TODO: Write error message about starting game with too many evils
        }
        // Don't need to check special good roles, since it's impossible
        // to have more special good roles than the total number of good roles
        let mut roles: Vec<Role> = vec![Role::Merlin, Role::Assassin];
        for role in &val.state.special_roles {
            roles.push(*role);
        }
        for _ in good_roles + 1..config.good_count {
            roles.push(Role::GoodGuy);
        }
        for _ in evil_roles + 1..config.evil_count {
            roles.push(Role::EvilGuy);
        }

        let mut players = val.players.clone();
        // Sanity check to see if roles to players is one to one
        if players.len() != roles.len() {
            return Err(()); // TODO: Add some error message for this sanity check
        }
        players.shuffle(&mut thread_rng());
        roles.shuffle(&mut thread_rng());

        let mut merlins_watch_list: HashSet<UserId> = HashSet::new();
        let mut percival_watch_list: HashSet<UserId> = HashSet::new();
        let mut evil_watch_list: HashSet<UserId> = HashSet::new();
        for i in 0..roles.len() {
            let role = roles[i];
            let role_num = role as i32;
            if role_num.abs() == 2 {
                percival_watch_list.insert(players[i]);
            }
            if role_num < 0 {
                if role_num < -1 {
                    merlins_watch_list.insert(players[i]);
                }
                evil_watch_list.insert(players[i]);
            }
        }
        println!("{:?}", val.players);
        println!("{:?}", roles);
        println!("{:?}", percival_watch_list);
        println!("{:?}", merlins_watch_list);
        println!("{:?}", evil_watch_list); 

        // Send out DMs
        // TODO: Once DM feature is done, add calls here

        // Randomly select king
        let turn_index = thread_rng().gen_range(0..val.players.len());

        // Randomly select lady index
        let lady_index = thread_rng().gen_range(0..val.players.len());

        // Generate new <Nominate> FSM struct
        Ok(AvalonFSM {
            host: val.host,
            players: val.players,
            roles,
            config,
            turn_index,
            lady_index,
            quests_passed: val.quests_passed,
            quests_failed: val.quests_failed,
            current_quest: val.current_quest,
            state: Nominate::new(0),
        })
    }
}

struct TeamVote {
    doom_counter: usize,
    nominated_players: HashSet<UserId>,
    votes: HashMap<UserId, Vote>,
}
impl TeamVote {
    fn new(doom_counter: usize, nominated_players: HashSet<UserId>) -> Self {
        TeamVote {
            doom_counter,
            nominated_players,
            votes: HashMap::new(),
        }
    }
}
impl TryFrom<AvalonFSM<Nominate>> for AvalonFSM<TeamVote> {
    type Error = ();

    fn try_from(val: AvalonFSM<Nominate>) -> Result<AvalonFSM<TeamVote>, Self::Error> {

    }
}

struct Questing {
    questers: HashSet<UserId>,
    votes: HashMap<UserId, Vote>,
}
impl Questing {
    fn new(questers: HashSet<UserId>) -> Self {
        Questing {
            questers,
            votes: HashMap::new(),
        }
    }
}

struct LastStand; 
impl LastStand {
    fn new() -> Self {
        LastStand
    }
}

struct GameOver;
impl GameOver {
    fn new() -> Self {
        GameOver
    }
}

#[tokio::main]
async fn main() {
    // !!! Remove once done with testing 
    /***********************************/
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