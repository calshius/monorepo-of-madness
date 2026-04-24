use std::sync::Arc;
use std::sync::atomic::{AtomicUsize, Ordering};
use anyhow::Result;
use rig::tool::Tool;
use serde::Deserialize;
use serde_json::json;
use reqwest;
use urlencoding;

/// Per-task web search tool. Each benchmark run gets its own instance with its
/// own counter so parallel runs don't share state.
pub struct SearchKnowledgeBase {
    pub counter: Arc<AtomicUsize>,
}



#[derive(Deserialize)]
pub struct SearchArgs {
    pub query: String,
}

#[derive(Debug, thiserror::Error)]
#[error("search error: {0}")]
pub struct SearchError(String);

impl Tool for SearchKnowledgeBase {
    const NAME: &'static str = "search_knowledge_base";
    type Error = SearchError;
    type Args = SearchArgs;
    type Output = String;

    async fn definition(&self, _prompt: String) -> rig::completion::ToolDefinition {
        rig::completion::ToolDefinition {
            name: Self::NAME.to_string(),
            description: "Search the web for information about a topic.".to_string(),
            parameters: json!({
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The topic to look up"
                    }
                },
                "required": ["query"]
            }),
        }
    }

    async fn call(&self, args: Self::Args) -> Result<Self::Output, Self::Error> {
        self.counter.fetch_add(1, Ordering::SeqCst);

        let url = format!(
            "https://api.duckduckgo.com/?q={}&format=json&no_html=1&skip_disambig=1",
            urlencoding::encode(&args.query)
        );

        let resp = reqwest::get(&url)
            .await
            .map_err(|e| SearchError(e.to_string()))?;

        let data: DdgResponse = resp
            .json()
            .await
            .map_err(|e| SearchError(e.to_string()))?;

        if let Some(text) = data.abstract_text.filter(|t| !t.is_empty()) {
            let source = data.abstract_source.unwrap_or_default();
            return Ok(if source.is_empty() {
                text
            } else {
                format!("{text} (Source: {source})")
            });
        }

        // Fall back to first few related topics
        if let Some(topics) = data.related_topics {
            let snippets: Vec<String> = topics
                .iter()
                .take(3)
                .filter_map(|t| t.get("Text")?.as_str().map(String::from))
                .collect();
            if !snippets.is_empty() {
                return Ok(snippets.join(" "));
            }
        }

        Ok(format!("No web results found for '{}'.", args.query))
    }
}

#[derive(Deserialize)]
struct DdgResponse {
    #[serde(rename = "AbstractText")]
    abstract_text: Option<String>,
    #[serde(rename = "AbstractSource")]
    abstract_source: Option<String>,
    #[serde(rename = "RelatedTopics")]
    related_topics: Option<Vec<serde_json::Value>>,
}