use std::sync::Arc;
use std::sync::atomic::{AtomicUsize, Ordering};
use anyhow::Result;
use rig::tool::Tool;
use serde::Deserialize;
use serde_json::json;

/// Per-task photosynthesis data collection tool. Each benchmark run gets its own instance.
pub struct PhotosynthesisDataCollector {
    pub counter: Arc<AtomicUsize>,
}



#[derive(Deserialize)]
pub struct PhotosynthesisArgs {
    pub flower_type: String,
}

#[derive(Debug, thiserror::Error)]
#[error("photosynthesis data error: {0}")]
pub struct PhotosynthesisError(String);

impl Tool for PhotosynthesisDataCollector {
    const NAME: &'static str = "photosynthesis_data_collector";
    type Error = PhotosynthesisError;
    type Args = PhotosynthesisArgs;
    type Output = String;

    async fn definition(&self, _prompt: String) -> rig::completion::ToolDefinition {
        rig::completion::ToolDefinition {
            name: Self::NAME.to_string(),
            description: "Collect specific data about photosynthesis in different flower types.".to_string(),
            parameters: json!({
                "type": "object",
                "properties": {
                    "flower_type": {
                        "type": "string",
                        "description": "Type of flower to get photosynthesis data for (e.g., 'rose', 'sunflower', 'orchid')"
                    }
                },
                "required": ["flower_type"]
            }),
        }
    }

    async fn call(&self, args: Self::Args) -> Result<Self::Output, Self::Error> {
        self.counter.fetch_add(1, Ordering::SeqCst);

        // Simulate specialized photosynthesis data collection
        let flower_data = [
            ("rose", "Roses perform C3 photosynthesis with optimal rates at 25°C. Their stomatal density varies by cultivar affecting CO2 uptake efficiency."),
            ("sunflower", "Sunflowers exhibit high photosynthetic rates due to large leaf area and heliotropic movement maximizing light capture. C3 pathway with Rubisco activity peaking midday."),
            ("orchid", "Orchids often use CAM photosynthesis in arid adaptations, opening stomata at night to reduce water loss while fixing CO2."),
            ("tomato", "Tomato plants show inducible C4-like photosynthesis under high light stress, with bundle sheath chloroplasts enhancing CO2 concentration."),
            ("maize", "Maize is a classic C4 plant with Kranz anatomy, showing 50% higher photosynthetic efficiency than C3 plants under high temperature and light."),
        ];

        let result = flower_data
            .iter()
            .find(|(ft, _)| ft.eq_ignore_ascii_case(&args.flower_type))
            .map(|(_, desc)| (*desc).to_string())
            .unwrap_or_else(|| format!("General photosynthesis data for {}: Involves light-dependent reactions producing ATP/NADPH, followed by Calvin cycle fixing CO2 into carbohydrates. Occurs in chloroplasts with chlorophyll absorbing light energy.", args.flower_type));

        Ok(result)
    }
}