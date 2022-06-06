use serde::Deserialize;
use std::collections::{HashMap, HashSet};
use std::env;
use std::fmt;
use std::fs;

use serenity::{
    async_trait,
    model::{channel::Message, gateway::Ready, id::UserId},
    prelude::*,
};

enum Stage {
    Created,
    Nominate,
    TeamVote,
    Questing,
    LastStand,
    GameOver,
}

enum Vote {
    Yea,
    Nay,
}

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

#[derive(Default)]
struct Player {
    id: UserId,
    role: Role,
}

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
    players: Vec<Player>,
    stage: Stage,

    king_privilege: Player,
    lady_privilege: Player,
    turn: i32,

    quests_passed: i32,
    quests_failed: i32,
    current_quest: i32,
    doom_counter: i32,
    questers_required: i32,
    double_fail: bool,
    questers: HashSet<Player>,
    voted: HashSet<Player>,

    merlins_watch_list: HashSet<Player>,
    evil_watch_list: HashSet<Player>,
    add_percival: bool,
    add_morgana: bool,
    add_mordred: bool,
    add_oberon: bool,
    add_lancelot: bool,
}

struct GameSession {
    host: UserId,
    involved_users: Vec<UserId>,
    state: GameState,
}

impl GameState {
    fn next_stage(&mut self) -> Result<&str, &str> {
        match self.stage {
            Stage::Created => {
                // ! Uncomment this block before pushing for testing/prod
                // if !self.player_count_check() {
                //     // TODO: add Discord message saying lack of players
                //     println!("Too few players!");
                //     return;
                // }
                // Get game configuration
                let data = fs::read_to_string("./settings.json").expect("Unable to open file");
                let mut config_map: HashMap<usize, GameConfig> = serde_json::from_str(data.as_str()).unwrap();
                let config = config_map.remove(&self.players.len());
                match config {
                    Some(valid_conf) => self.config = valid_conf,
                    None => return Err("Configuration loaded is malformed or not valid. Please redownload the settings.json file."),
                }


                // Assign roles 

                // send out DMs 
                // randomly select king
                // change stage to nominate
            },
            Stage::Nominate => {

            },
            Stage::TeamVote => {

            },
            Stage::Questing => {

            },
            Stage::LastStand => {

            },
            Stage::GameOver => {
                
            }
        }

        // TODO: Change this message and use it for logging in the future.
        Ok("Progressed to next stage")
    }

    fn add_player(&mut self, id: UserId) {
        self.players.push(Player {
            id,
            role: Role::default(),
        })
    }

    fn player_count_check(&self) -> bool {
        self.players.len() >= 5
    }
}

fn build_player(id: UserId, role: Role) -> Player {
    Player {
        id,
        role,
    }
}

fn build_game() -> GameState {
    GameState {
        config: GameConfig::default(),
        players: Vec::new(),
        stage: Stage::Created,
        king_privilege: Player::default(),
        lady_privilege: Player::default(),
        turn: 0,
        quests_passed: 0,
        quests_failed: 0,
        current_quest: 0,
        doom_counter: 0,
        questers_required: 0,
        double_fail: false,
        questers: HashSet::new(),
        voted: HashSet::new(),
        merlins_watch_list: HashSet::new(),
        evil_watch_list: HashSet::new(),
        add_percival: false,
        add_morgana: false,
        add_mordred: false,
        add_oberon: false,
        add_lancelot: false,
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
    let mut game: GameState = build_game();
    // TODO: Use this Result for logging and/or stopping the game without crashing the bot
    game.next_stage();
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