from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]


def load_module(name: str, relative_path: str):
    module_path = ROOT_DIR / relative_path
    spec = importlib.util.spec_from_file_location(name, module_path)

    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module: {module_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


research_tools = load_module(
    "research_tools",
    "01_research_agent/tools.py",
)
expense_tools = load_module(
    "expense_tools",
    "02_expense_agent/tools.py",
)
text_tools = load_module(
    "text_tools",
    "03_text_analysis_agent/tools.py",
)
file_tools = load_module(
    "file_tools",
    "04_file_organizer_agent/tools.py",
)
dataset_tools = load_module(
    "dataset_tools",
    "05_dataset_inspector_agent/tools.py",
)
study_tools = load_module(
    "study_tools",
    "06_study_planner_agent/tools.py",
)
code_tools = load_module(
    "code_tools",
    "07_code_reviewer_agent/tools.py",
)
notes_tools = load_module(
    "notes_tools",
    "08_notes_agent/tools.py",
)
product_tools = load_module(
    "product_tools",
    "09_product_comparison_agent/tools.py",
)
statistics_tools = load_module(
    "statistics_tools",
    "10_statistics_agent/tools.py",
)


class ResearchToolTests(unittest.TestCase):
    def test_extract_arxiv_id_from_url(self) -> None:
        result = research_tools._extract_arxiv_id(
            "https://arxiv.org/abs/2406.09714"
        )

        self.assertEqual(result, "2406.09714")

    def test_extract_arxiv_id_from_plain_id(self) -> None:
        result = research_tools._extract_arxiv_id("arXiv:2406.09714")

        self.assertEqual(result, "2406.09714")

    def test_calculate_paper_age(self) -> None:
        result = research_tools.calculate_paper_age("2020-01-01")

        self.assertIn("2020-01-01", result)
        self.assertIn("days old", result)


class ExpenseToolTests(unittest.TestCase):
    def setUp(self) -> None:
        expense_tools._EXPENSES.clear()

    def test_add_and_total_expenses(self) -> None:
        expense_tools.add_expense(
            json.dumps(
                {
                    "description": "Coffee",
                    "amount": 4.50,
                    "category": "food",
                }
            )
        )

        expense_tools.add_expense(
            json.dumps(
                {
                    "description": "Notebook",
                    "amount": 5.50,
                    "category": "study",
                }
            )
        )

        result = expense_tools.calculate_total("{}")

        self.assertIn("$10.00", result)
        self.assertIn("2 expense(s)", result)

    def test_check_budget(self) -> None:
        expense_tools.add_expense(
            json.dumps(
                {
                    "description": "Lunch",
                    "amount": 12,
                    "category": "food",
                }
            )
        )

        result = expense_tools.check_budget(
            json.dumps(
                {
                    "budget": 20,
                    "category": "food",
                }
            )
        )

        self.assertIn("within budget", result)
        self.assertIn("$8.00", result)


class TextAnalysisToolTests(unittest.TestCase):
    def test_count_text(self) -> None:
        result = text_tools.count_text(
            json.dumps(
                {
                    "text": "AI agents use tools. They can act."
                }
            )
        )

        self.assertIn("Words: 7", result)
        self.assertIn("Sentences: 2", result)

    def test_extract_keywords(self) -> None:
        result = text_tools.extract_keywords(
            json.dumps(
                {
                    "text": "Agents use tools. Agents can select tools.",
                    "limit": 2,
                }
            )
        )

        self.assertIn("agents (2)", result)
        self.assertIn("tools (2)", result)

    def test_reading_time(self) -> None:
        result = text_tools.calculate_reading_time(
            json.dumps(
                {
                    "text": "one two three four",
                    "words_per_minute": 200,
                }
            )
        )

        self.assertIn("1 minute(s)", result)


class FileOrganizerToolTests(unittest.TestCase):
    def test_classify_and_preview_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            (directory / "photo.png").write_text("image", encoding="utf-8")
            (directory / "notes.txt").write_text("notes", encoding="utf-8")
            (directory / "script.py").write_text("print('hi')", encoding="utf-8")

            tool_input = json.dumps(
                {
                    "directory": str(directory),
                }
            )

            classification = file_tools.classify_files(tool_input)
            preview = file_tools.preview_organization(tool_input)

            self.assertIn("images:", classification)
            self.assertIn("documents:", classification)
            self.assertIn("code:", classification)
            self.assertIn("photo.png -> images/photo.png", preview)

    def test_organize_files_requires_confirmation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            (directory / "notes.txt").write_text("notes", encoding="utf-8")

            with self.assertRaises(ValueError):
                file_tools.organize_files(
                    json.dumps(
                        {
                            "directory": str(directory),
                            "confirm": False,
                        }
                    )
                )

    def test_organize_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            (directory / "notes.txt").write_text("notes", encoding="utf-8")

            file_tools.organize_files(
                json.dumps(
                    {
                        "directory": str(directory),
                        "confirm": True,
                    }
                )
            )

            self.assertTrue(
                (directory / "documents" / "notes.txt").exists()
            )


class DatasetInspectorToolTests(unittest.TestCase):
    def setUp(self) -> None:
        dataset_tools._DATASET = None
        dataset_tools._DATASET_PATH = None

    def test_load_and_inspect_csv(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            csv_path = Path(temporary_directory) / "sample.csv"
            csv_path.write_text(
                "name,age,score\n"
                "Alice,25,88\n"
                "Bob,,92\n"
                "Cara,30,85\n",
                encoding="utf-8",
            )

            load_result = dataset_tools.load_csv(
                json.dumps(
                    {
                        "path": str(csv_path),
                    }
                )
            )

            shape_result = dataset_tools.get_dataset_shape("{}")
            columns_result = dataset_tools.get_column_names("{}")
            missing_result = dataset_tools.calculate_missing_values(
                json.dumps(
                    {
                        "column": "age",
                    }
                )
            )

            self.assertIn("3 rows and 3 columns", load_result)
            self.assertIn("Rows: 3", shape_result)
            self.assertIn("Columns: 3", shape_result)
            self.assertIn("name", columns_result)
            self.assertIn("Missing values: 1", missing_result)

    def test_summarize_numeric_column(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            csv_path = Path(temporary_directory) / "sample.csv"
            csv_path.write_text(
                "value\n10\n20\n30\n",
                encoding="utf-8",
            )

            dataset_tools.load_csv(
                json.dumps(
                    {
                        "path": str(csv_path),
                    }
                )
            )

            result = dataset_tools.summarize_column(
                json.dumps(
                    {
                        "column": "value",
                    }
                )
            )

            self.assertIn("Mean: 20.0000", result)
            self.assertIn("Median: 20.0000", result)


class StudyPlannerToolTests(unittest.TestCase):
    def test_estimate_topic_hours(self) -> None:
        result = study_tools.estimate_topic_hours(
            json.dumps(
                {
                    "topics": [
                        {
                            "name": "Arrays",
                            "difficulty": "easy",
                        },
                        {
                            "name": "Graphs",
                            "difficulty": "hard",
                        },
                    ]
                }
            )
        )

        self.assertIn("Arrays: 2.0 hour(s)", result)
        self.assertIn("Graphs: 7.0 hour(s)", result)
        self.assertIn("9.0 hours", result)

    def test_create_study_schedule(self) -> None:
        result = study_tools.create_study_schedule(
            json.dumps(
                {
                    "topics": [
                        {
                            "name": "Arrays",
                            "hours": 2,
                        },
                        {
                            "name": "Graphs",
                            "hours": 3,
                        },
                    ],
                    "start_date": "2026-08-01",
                    "daily_hours": 2,
                }
            )
        )

        self.assertIn("Day 1 — 2026-08-01", result)
        self.assertIn("Plan length: 3 day(s)", result)


class CodeReviewerToolTests(unittest.TestCase):
    def test_review_valid_python_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            file_path = Path(temporary_directory) / "sample.py"
            file_path.write_text(
                '"""Sample module."""\n\n'
                "def add(a, b):\n"
                '    """Return the sum."""\n'
                "    return a + b\n",
                encoding="utf-8",
            )

            result = code_tools.review_python_file(
                json.dumps(
                    {
                        "path": str(file_path),
                    }
                )
            )

            self.assertIn("No syntax errors", result)
            self.assertIn("Functions: add", result)
            self.assertIn("No missing docstrings", result)

    def test_detect_syntax_error(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            file_path = Path(temporary_directory) / "broken.py"
            file_path.write_text(
                "def broken(\n",
                encoding="utf-8",
            )

            result = code_tools.check_syntax(
                json.dumps(
                    {
                        "path": str(file_path),
                    }
                )
            )

            self.assertIn("Syntax error", result)


class NotesToolTests(unittest.TestCase):
    def test_list_search_and_open_notes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            note_path = directory / "research.md"

            note_path.write_text(
                "# Research\n\nConformal prediction provides coverage guarantees.",
                encoding="utf-8",
            )

            list_result = notes_tools.list_notes(
                json.dumps(
                    {
                        "directory": str(directory),
                    }
                )
            )

            search_result = notes_tools.search_notes(
                json.dumps(
                    {
                        "directory": str(directory),
                        "query": "coverage guarantees",
                    }
                )
            )

            open_result = notes_tools.open_note(
                json.dumps(
                    {
                        "directory": str(directory),
                        "filename": "research.md",
                    }
                )
            )

            self.assertIn("research.md", list_result)
            self.assertIn("coverage guarantees", search_result)
            self.assertIn("Conformal prediction", open_result)


class ProductComparisonToolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.products = [
            {
                "name": "Product A",
                "price": 80,
                "rating": 4.5,
                "features": ["lightweight", "wireless"],
            },
            {
                "name": "Product B",
                "price": 60,
                "rating": 4.0,
                "features": ["wireless"],
            },
        ]

    def test_find_cheapest_product(self) -> None:
        result = product_tools.find_cheapest_product(
            json.dumps(
                {
                    "products": self.products,
                }
            )
        )

        self.assertIn("Product B", result)
        self.assertIn("$60.00", result)

    def test_filter_by_budget(self) -> None:
        result = product_tools.filter_by_budget(
            json.dumps(
                {
                    "budget": 70,
                    "products": self.products,
                }
            )
        )

        self.assertIn("Product B", result)
        self.assertNotIn("Product A:", result)


class StatisticsToolTests(unittest.TestCase):
    def test_descriptive_statistics(self) -> None:
        result = statistics_tools.calculate_descriptive_statistics(
            json.dumps(
                {
                    "values": [10, 20, 30],
                }
            )
        )

        self.assertIn("Mean: 20.0000", result)
        self.assertIn("Median: 20.0000", result)

    def test_z_score(self) -> None:
        result = statistics_tools.calculate_z_score(
            json.dumps(
                {
                    "value": 85,
                    "mean": 70,
                    "standard_deviation": 10,
                }
            )
        )

        self.assertIn("Z-score: 1.5000", result)
        self.assertIn("above", result)

    def test_confusion_matrix_metrics(self) -> None:
        result = statistics_tools.calculate_confusion_matrix_metrics(
            json.dumps(
                {
                    "true_positive": 40,
                    "false_positive": 10,
                    "true_negative": 35,
                    "false_negative": 5,
                }
            )
        )

        self.assertIn("Accuracy:", result)
        self.assertIn("Precision:", result)
        self.assertIn("Recall:", result)
        self.assertIn("F1 score:", result)

    def test_correlation(self) -> None:
        result = statistics_tools.calculate_correlation(
            json.dumps(
                {
                    "x": [1, 2, 3, 4],
                    "y": [2, 4, 6, 8],
                }
            )
        )

        self.assertIn("Pearson correlation: 1.0000", result)
        self.assertIn("strong positive", result)


if __name__ == "__main__":
    unittest.main()