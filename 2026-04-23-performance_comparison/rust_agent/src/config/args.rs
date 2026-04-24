use std::env;
use std::path::PathBuf;

pub struct Config {
    pub runs: usize,
    pub model: String,
    pub output: PathBuf,
}

impl Config {
    pub fn from_env() -> Self {
        let args: Vec<String> = env::args().collect();
        let runs = args
            .iter()
            .position(|a| a == "--runs")
            .and_then(|i| args.get(i + 1))
            .and_then(|s| s.parse().ok())
            .unwrap_or(5);

        let model = args
            .iter()
            .position(|a| a == "--model")
            .and_then(|i| args.get(i + 1))
            .cloned()
            .unwrap_or_else(|| "nvidia/nemotron-3-super-120b-a12b:free".to_string());

        let default_output = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join(format!(
            "../benchmark/results/rust_results_{}.jsonl",
            model_slug(&model)
        ));

        let output = args
            .iter()
            .position(|a| a == "--output")
            .and_then(|i| args.get(i + 1))
            .map(PathBuf::from)
            .unwrap_or(default_output);

        Config {
            runs,
            model,
            output,
        }
    }
}

fn model_slug(model: &str) -> String {
    let name = model.split('/').last().unwrap_or(model);
    let name = name.split(':').next().unwrap_or(name);
    name.to_string()
}
