use serde::Deserialize;
use rig::agent::Agent;
use rig::completion::{CompletionModel, Prompt};

#[derive(Deserialize)]
pub struct EvalResult {
    pub accuracy: i32,
    pub completeness: i32,
    pub reasoning: String,
}

const EVAL_PROMPT_TEMPLATE: &str = r#"You are an expert biology teacher evaluating an answer comparing photosynthesis in different flower types.

Key concepts that a complete, accurate answer should cover:
1. Basic photosynthesis process: Light energy conversion to chemical energy (glucose / ATP)
2. Reactants and products: CO2 and H2O as inputs, glucose (C6H12O6) and O2 as outputs
3. Cellular location: chloroplasts (thylakoid membranes and stroma) where photosynthesis occurs
4. Two-stage process: light-dependent reactions and Calvin cycle (light-independent reactions)
5. Photosynthetic pathways: Differences between C3, C4, and CAM mechanisms
6. Environmental adaptations: How different flowers adapt photosynthesis to their environments (light, water, temperature)
7. Structural variations: Leaf anatomy differences affecting photosynthetic efficiency between species
8. Comparative analysis: Specific differences between rose and sunflower photosynthesis capabilities

Answer to evaluate:
{answer}

Score the answer on two dimensions from 0 to 5:
- accuracy: Is the information factually correct? (0=completely wrong, 5=fully accurate)
- completeness: How well does the answer cover the 8 key concepts above? (0=none, 5=exceptionally thorough coverage)

Respond ONLY with JSON on a single line, no markdown:
{"accuracy": <int 0-5>, "completeness": <int 0-5>, "reasoning": "<one sentence>"}"#;

pub async fn evaluate_answer(
    eval_agent: &Agent<impl CompletionModel + 'static>,
    answer: &str,
) -> EvalResult {
    let prompt = EVAL_PROMPT_TEMPLATE.replace("{answer}", answer);

    match eval_agent.prompt(&prompt).await {
        Ok(response) => {
            // Extract the JSON object from the response
            if let Some(start) = response.find('{') {
                if let Some(end) = response.rfind('}') {
                    let json_str = &response[start..=end];
                    if let Ok(result) = serde_json::from_str::<EvalResult>(json_str) {
                        return result;
                    }
                }
            }
            EvalResult {
                accuracy: -1,
                completeness: -1,
                reasoning: "eval parse error".to_string(),
            }
        }
        Err(e) => EvalResult {
            accuracy: -1,
            completeness: -1,
            reasoning: format!("eval call error: {e}"),
        },
    }
}