import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from .models import AppUser, Dish, CookedDish
import random

class RecommendationSystem:
    def __init__(self, user_id):
        self.user_id = user_id
        self.prepare_data()
        self.learning_rate = 0.1
        self.recommendation_history = []
        self.feedback_data = pd.DataFrame()  # Replace with your actual data initialization logic



    def prepare_data(self):
        self.users = list(AppUser.objects.all())
        self.dishes = list(Dish.objects.all())
        self.user_features = self.create_user_feature_matrix()
        self.dish_features = self.create_dish_feature_matrix()
        self.similarity_matrix = cosine_similarity(self.user_features, self.dish_features)


    def create_user_feature_matrix(self):
        user_data = []
        for user in self.users:
            preferences = user.meal_preference or []
            features = [
                int('appetizer' in preferences),
                int('soup and pasta/noodles' in preferences),
                int('vegetable_recipe' in preferences),
                int('seafood_recipe' in preferences),
                int('meat_recipe' in preferences),
                int('dessert' in preferences),
            ]
            user_data.append(features)
        return np.array(user_data)


    def create_dish_feature_matrix(self):
        dish_data = []
        for dish in self.dishes:
            features = [
                int(dish.meal_type.filter(name='appetizer').exists()),
                int(dish.meal_type.filter(name='soup and pasta/noodles').exists()),
                int(dish.meal_type.filter(name='vegetable_recipe').exists()),
                int(dish.meal_type.filter(name='seafood_recipe').exists()),
                int(dish.meal_type.filter(name='meat_recipe').exists()),
                int(dish.meal_type.filter(name='dessert').exists()),
            ]
            dish_data.append(features)
        return np.array(dish_data)


    def get_recommendations(self, top_n=100, epsilon=0.2):
        try:
            user = next((user for user in self.users if user.id == self.user_id), None)
            if user is None:
                print(f"User ID {self.user_id} not found.")
                return []

            user_index = self.users.index(user)
            meal_type_match_scores = self.compute_meal_type_match_scores(user, self.dishes)
            combined_scores = self.similarity_matrix[user_index] + meal_type_match_scores

            # Epsilon-greedy strategy: explore new recommendations with epsilon probability
            if random.random() < epsilon:
                top_n_indices = np.random.choice(len(self.dishes), top_n, replace=False)
            else:
                top_n_indices = np.argsort(combined_scores)[-top_n:][::-1]

            recommendations = [self.dishes[i] for i in top_n_indices if i < len(self.dishes)]

            # Apply filters
            recommendations = self.filter_by_allergies(recommendations, user.allergies)
            recommendations = self.filter_by_servings(recommendations, user.family_size)
            recommendations = self.filter_by_age_range(recommendations, user.age_range)
            recommendations = self.filter_by_cooking_skills(recommendations, user.cooking_skills)
            recommendations = self.get_unique_recommendations(user, recommendations)

            # Exclude already cooked dishes
            recommendations = self.exclude_cooked_dishes(recommendations)

            updated_recommendations = self.update_recommendations(user, recommendations)
            self.calculate_accuracy_metrics(updated_recommendations)
            return updated_recommendations

        except Exception as e:
            print(f"An error occurred: {e}")
            return []

    def exclude_cooked_dishes(self, recommendations):
        # Get dishes the user has already cooked
        cooked_dishes = set(self.get_user_liked_dishes())
        # Filter out cooked dishes from recommendations
        return [dish for dish in recommendations if dish.dish_name not in cooked_dishes]


    def compute_meal_type_match_scores(self, user, dishes):
        # Standardize user preferences to lowercase
        user_preferences = [preference.lower() for preference in (user.meal_preference or [])]
        meal_type_match_scores = np.zeros(len(dishes))

        print(f"User Preferences (Meal Types): {user_preferences}")

        for i, dish in enumerate(dishes):
            # Get and standardize the dish's meal types to lowercase
            dish_meal_types = [mt.name.lower() for mt in dish.meal_type.all()]

            # Check if any user preference matches a dish meal type
            match_score = any(preference in dish_meal_types for preference in user_preferences)

            # Prioritize dishes that match user preferences by setting match score to 1
            if match_score:
                meal_type_match_scores[i] = 2

            # Debug output for each dish's meal types and match score
            print(f"Dish '{dish.dish_name}' Meal Types: {dish_meal_types}")
            print(f"Match Score for '{dish.dish_name}': {meal_type_match_scores[i]}")
       
        print("Final Meal Type Match Scores:", meal_type_match_scores)
        return meal_type_match_scores


    def filter_by_allergies(self, recommendations, allergies):
        allergies = allergies or []
        filtered_recommendations = []
        eliminated_count = 0  # Counter for eliminated dishes


        for dish in recommendations:
            dish_ingredients = dish.ingredient_list or []


            if isinstance(dish_ingredients[0], dict):
                ingredient_strings = [ingredient.get('ingredient', '') for ingredient in dish_ingredients]
            else:
                ingredient_strings = dish_ingredients


            ingredient_string = " ".join(ingredient_strings).lower()
            if not any(allergen.lower() in ingredient_string for allergen in allergies):
                filtered_recommendations.append(dish)
            else:
                eliminated_count += 1


        print(f"Number of dishes not recommended due to allergies: {eliminated_count}")
        return filtered_recommendations


    def filter_by_servings(self, recommendations, family_size):
        if family_size is None:
            return recommendations


        filtered_recommendations = []
        print(f"Original family size input: {family_size}")
        family_size = family_size.strip().replace(' Members', '')
        print(f"Filtered family size: {family_size}")


        family_min, family_max = self.parse_family_size(family_size)


        for dish in recommendations:
            dish_min, dish_max = self.parse_family_size(dish.number_of_servings)


            if dish_min <= family_max and dish_max >= family_min:
                filtered_recommendations.append(dish)


        print(f"Number of dishes filtered by servings: {len(recommendations) - len(filtered_recommendations)}")
        print(f"Filtered recommendations: {[dish.dish_name for dish in filtered_recommendations]}")


        return filtered_recommendations


    def parse_family_size(self, size_str):
        if size_str:
            parts = size_str.split('-')
            if len(parts) == 2:
                return int(parts[0]), int(parts[1])
        return 0, 0


    def filter_by_age_range(self, recommendations, user_age_range):
        if not user_age_range:
            return recommendations


        filtered_recommendations = []
        user_age_ranges = [age.lower() for age in user_age_range]


        print(f"Filtering for user age range: {user_age_ranges}")


        for dish in recommendations:
            dish_age_ranges = [age.lower() for age in dish.age_range_that_can_eat]


            print(f"Checking dish: {dish.dish_name} with allowed age ranges: {dish_age_ranges}")


            matches = set(user_age_ranges) & set(dish_age_ranges)


            if matches:
                filtered_recommendations.append(dish)
                print(f"Matched dish: {dish.dish_name}")


        print(f"Number of dishes filtered by age range: {len(recommendations) - len(filtered_recommendations)}")
        print(f"Filtered recommendations: {[dish.dish_name for dish in filtered_recommendations]}")


        return filtered_recommendations


    def filter_by_cooking_skills(self, recommendations, cooking_skills):
        if not cooking_skills:
            return recommendations


        filtered_recommendations = []


        # Define skill levels and their corresponding accessible levels
        skill_hierarchy = {
            "beginner": ["beginner"],
            "intermediate": ["beginner", "intermediate"],
            "advanced": ["beginner", "intermediate", "advanced"],
        }


        # Get the levels accessible to the user's skill level
        user_accessible_skills = skill_hierarchy.get(cooking_skills.lower(), [])


        for dish in recommendations:
            required_skills = dish.skills_needed.lower()
            if required_skills in user_accessible_skills:
                filtered_recommendations.append(dish)


        return filtered_recommendations


    def update_recommendations(self, user, recommendations):
        for dish in recommendations:
            reward = self.reward_function(user, dish)
            self.recommendation_history.append((user.id, dish.dish_name, reward))

            # Gradual update to similarity matrix
            user_index = self.users.index(user)
            dish_index = self.dishes.index(dish)
            self.similarity_matrix[user_index, dish_index] += self.learning_rate * (reward - self.similarity_matrix[user_index, dish_index])

        return recommendations



    def reward_function(self, user, recommended_dish):
        liked_dishes = self.get_user_liked_dishes()
        if recommended_dish.dish_name in liked_dishes:
            return 1  # Full match
        elif recommended_dish in self.get_partial_matches(user):
            return 0.5  # Partial match
        else:
            return -1  # No match

    def get_partial_matches(self, user):
        # This function checks for partial matches, e.g., based on ingredients or meal types.
        # Adjust to whatever criteria you'd like as partial satisfaction indicators.
        partial_matches = []
        user_preferences = set(user.meal_preference or [])
        for dish in self.dishes:
            dish_preferences = set(dish.meal_type.values_list('name', flat=True))
            if user_preferences & dish_preferences:
                partial_matches.append(dish)
        return partial_matches


    def get_unique_recommendations(self, user, recommendations):
        # Get past recommendations from history
        past_dishes = {rec[1] for rec in self.recommendation_history if rec[0] == user.id}
        return [dish for dish in recommendations if dish.dish_name not in past_dishes]



    def calculate_accuracy_metrics(self, recommendations):
        # Retrieve the dishes the user liked
        liked_dishes = set(self.get_user_liked_dishes())

        # Ensure recommendations are treated as a set of dish names and IDs for comparison
        recommended_dish_names = {dish.dish_name for dish in recommendations}
        recommended_dish_ids = {dish.id for dish in recommendations}  # Assuming 'id' is the unique identifier

        # Check if feedback_df exists
        if not hasattr(self, 'feedback_df'):
            print("Error: Feedback data is not available.")
            return

        # Get user feedback for calculating positive feedback
        user_feedback = self.feedback_df[self.feedback_df['userid'] == self.user_id]
        positive_feedback = set(user_feedback[user_feedback['rating'] >= 3]['dishid'])

        # Calculate true positives, false positives, and false negatives
        true_positives = len(recommended_dish_ids & positive_feedback)
        false_positives = len(recommended_dish_ids - positive_feedback)
        false_negatives = len(positive_feedback - recommended_dish_ids)

        # Calculate precision and recall, with checks to avoid division by zero
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0
        f1_score = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        # Output metrics in the specified format
        print(f"User ID: {self.user_id}")
        print(f"Recommendations Count: {len(recommended_dish_names)}")
        print(f"Liked Dishes Count: {len(liked_dishes)}")
        print(f"True Positives: {true_positives}")
        print(f"Precision: {precision:.2f}")
        print(f"Recall: {recall:.2f}")
        print(f"F1 Score: {f1_score:.2f}")
        print("User Liked Dishes:", liked_dishes)
        print("Recommended Dishes:", recommended_dish_names)
        
        # Additional output for recommendations list and community picks count
        print("Recommendations:", list(recommended_dish_names))
        print(f"Number of recommendations: {len(recommended_dish_names)}")
        print(f"Top community picks count: {min(10, len(recommended_dish_names))}")  # assuming 10 is the max for community picks

    def get_user_liked_dishes(self):
        return list(CookedDish.objects.filter(user_id=self.user_id, cooked=True).values_list('dish__dish_name', flat=True))
