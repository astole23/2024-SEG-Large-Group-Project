from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch

from tutorials.helpers import (
    base_helpers, company_helpers, matchmaking_helper
)


class UtilityFunctionTests(TestCase):

    # === clean_location ===
    def test_clean_location_exact_city(self):
        self.assertEqual(matchmaking_helper.clean_location("London"), "London")

    def test_clean_location_with_comma(self):
        self.assertEqual(matchmaking_helper.clean_location("London, UK"), "London")

    def test_clean_location_unknown_city(self):
        self.assertEqual(matchmaking_helper.clean_location("Atlantis"), "Atlantis")

    def test_clean_location_none_input(self):
        self.assertIsNone(matchmaking_helper.clean_location(None))

    # === is_location_match ===
    def test_is_location_match_exact_match(self):
        self.assertEqual(matchmaking_helper.is_location_match(["London"], "London"), 0.5)

    def test_is_location_match_region_match(self):
        self.assertEqual(matchmaking_helper.is_location_match(["Manchester"], "Salford"), 0.5)

    def test_is_location_match_no_match(self):
        self.assertEqual(matchmaking_helper.is_location_match(["Cardiff"], "London"), -0.5)

    def test_is_location_match_with_none_values(self):
        self.assertEqual(matchmaking_helper.is_location_match([], "London"), -0.5)
        self.assertEqual(matchmaking_helper.is_location_match(["London"], None), -0.5)

    # === cosine_similarity_manual ===
    def test_cosine_similarity_identical_vectors(self):
        self.assertEqual(round(matchmaking_helper.cosine_similarity_manual([1, 0], [1, 0]), 5), 1.0)

    def test_cosine_similarity_orthogonal_vectors(self):
        self.assertEqual(round(matchmaking_helper.cosine_similarity_manual([1, 0], [0, 1]), 5), 0.0)

    def test_cosine_similarity_with_zero_vector(self):
        self.assertEqual(matchmaking_helper.cosine_similarity_manual([0, 0], [1, 2]), 0.0)

    # === get_embeddings ===
    @patch("tutorials.helpers.matchmaking_helper.together.Embeddings.create")
    def test_get_embeddings_success(self, mock_create):
    # This mocks the actual API call inside get_embeddings()
        mock_create.return_value = {
            "data": [
                {"embedding": [0.1, 0.2]},
                {"embedding": [0.3, 0.4]}
            ]
        }

    # Now we call the real function, which will use the mocked API
        result = matchmaking_helper.get_embeddings(["hello", "world"])

        # We expect the processed embeddings, not the raw dict
        self.assertEqual(result, [[0.1, 0.2], [0.3, 0.4]])

    @patch("tutorials.helpers.matchmaking_helper.together.Embeddings.create")
    def test_get_embeddings_error(self, mock_create):
        mock_create.side_effect = Exception("API Failure")
        result = matchmaking_helper.get_embeddings(["hello", "world"])
        self.assertEqual(result, [])

    def test_get_embeddings_invalid_input(self):
        self.assertEqual(matchmaking_helper.get_embeddings(["valid", 123]), [])
        self.assertEqual(matchmaking_helper.get_embeddings([]), [])

    # === match_job_to_cv_together ===
    @patch("tutorials.helpers.matchmaking_helper.get_embeddings")
    def test_match_job_to_cv_together_success(self, mock_get_embeddings):
        mock_get_embeddings.return_value = [
            [1, 0],
            [0.9, 0.1],
            [0.1, 0.9],
        ]
        result = matchmaking_helper.match_job_to_cv_together(
            ["Python developer with backend experience"],
            ["Backend Engineer", "Fullstack Developer"]
    )
        self.assertEqual(len(result), 2)
        self.assertIn("Backend Engineer", [title for title, _ in result])

    @patch("tutorials.helpers.matchmaking_helper.get_embeddings")
    def test_match_job_to_cv_together_empty_embeddings(self, mock_embeddings):
        mock_embeddings.return_value = []
        result = matchmaking_helper.match_job_to_cv_together(["Some CV"], ["Job A"])
        self.assertEqual(result, [])

    def test_match_job_to_cv_together_missing_input(self):
        self.assertEqual(matchmaking_helper.match_job_to_cv_together([], ["Job A"]), [])
        self.assertEqual(matchmaking_helper.match_job_to_cv_together(["Some CV"], []), [])