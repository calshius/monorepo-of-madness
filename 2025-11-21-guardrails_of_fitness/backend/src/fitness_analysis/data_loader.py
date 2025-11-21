"""Data loading utilities for Garmin and MyFitnessPal data."""

import pandas as pd
from pathlib import Path
from typing import Dict, Any
from datetime import datetime


class FitnessDataLoader:
    """Load and process fitness data from CSV files."""
    
    def __init__(self, data_dir: str = "/home/callum/projects/data"):
        self.data_dir = Path(data_dir)
        self.garmin_path = self.data_dir / "garmin" / "garmin.csv"
        self.mfp_nutrition_path = self.data_dir / "mfp" / "Nutrition-Summary-2024-11-11-to-2025-11-21.csv"
        self.mfp_exercise_path = self.data_dir / "mfp" / "Exercise-Summary-2024-11-11-to-2025-11-21.csv"
        self.mfp_measurement_path = self.data_dir / "mfp" / "Measurement-Summary-2024-11-11-to-2025-11-21.csv"
        
    def load_garmin_data(self) -> pd.DataFrame:
        """Load Garmin activity data."""
        df = pd.read_csv(self.garmin_path)
        df['Date'] = pd.to_datetime(df['Date'])
        return df
    
    def load_nutrition_data(self) -> pd.DataFrame:
        """Load MyFitnessPal nutrition data."""
        df = pd.read_csv(self.mfp_nutrition_path)
        df['Date'] = pd.to_datetime(df['Date'])
        return df
    
    def load_exercise_data(self) -> pd.DataFrame:
        """Load MyFitnessPal exercise data."""
        df = pd.read_csv(self.mfp_exercise_path)
        df['Date'] = pd.to_datetime(df['Date'])
        return df
    
    def load_measurement_data(self) -> pd.DataFrame:
        """Load MyFitnessPal measurement data."""
        df = pd.read_csv(self.mfp_measurement_path)
        df['Date'] = pd.to_datetime(df['Date'])
        return df
    
    def get_nutrition_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get summary statistics for nutrition data."""
        df = self.load_nutrition_data()
        recent_df = df[df['Date'] >= (datetime.now() - pd.Timedelta(days=days))]
        
        # Group by date and sum up daily totals
        daily_totals = recent_df.groupby('Date').agg({
            'Calories': 'sum',
            'Protein (g)': 'sum',
            'Carbohydrates (g)': 'sum',
            'Fat (g)': 'sum',
            'Fiber': 'sum',
            'Sugar': 'sum',
        }).reset_index()
        
        return {
            "avg_calories": daily_totals['Calories'].mean(),
            "avg_protein": daily_totals['Protein (g)'].mean(),
            "avg_carbs": daily_totals['Carbohydrates (g)'].mean(),
            "avg_fat": daily_totals['Fat (g)'].mean(),
            "avg_fiber": daily_totals['Fiber'].mean(),
            "avg_sugar": daily_totals['Sugar'].mean(),
            "days_analyzed": len(daily_totals),
        }
    
    def get_activity_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get summary statistics for Garmin activity data."""
        df = self.load_garmin_data()
        recent_df = df[df['Date'] >= (datetime.now() - pd.Timedelta(days=days))]
        
        return {
            "total_activities": len(recent_df),
            "avg_calories_burned": recent_df['Calories'].astype(float).mean(),
            "total_calories_burned": recent_df['Calories'].astype(float).sum(),
            "avg_heart_rate": recent_df['Avg HR'].astype(float).mean(),
            "activity_types": recent_df['Activity Type'].value_counts().to_dict(),
            "days_analyzed": days,
        }
    
    def get_combined_summary(self, days: int = 30) -> str:
        """Get a combined summary of all fitness data for LLM analysis."""
        nutrition = self.get_nutrition_summary(days)
        activity = self.get_activity_summary(days)
        
        summary = f"""
# Fitness Data Summary (Last {days} days)

## Nutrition Data:
- Average daily calories: {nutrition['avg_calories']:.1f} kcal
- Average daily protein: {nutrition['avg_protein']:.1f}g
- Average daily carbohydrates: {nutrition['avg_carbs']:.1f}g
- Average daily fat: {nutrition['avg_fat']:.1f}g
- Average daily fiber: {nutrition['avg_fiber']:.1f}g
- Average daily sugar: {nutrition['avg_sugar']:.1f}g
- Days with nutrition data: {nutrition['days_analyzed']}

## Activity Data:
- Total workouts: {activity['total_activities']}
- Average calories burned per workout: {activity['avg_calories_burned']:.1f} kcal
- Total calories burned: {activity['total_calories_burned']:.1f} kcal
- Average heart rate during workouts: {activity['avg_heart_rate']:.1f} bpm
- Activity types: {activity['activity_types']}
"""
        return summary
