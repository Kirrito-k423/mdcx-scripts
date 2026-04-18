import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tools.rename import checkmp4


class CheckMp4Tests(unittest.TestCase):
    def test_checkmp4_uses_next_available_cd_number_when_cd_targets_exist(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            source_file = folder / "SAVR-928-8K.mp4"
            existing_cd1 = folder / "SAVR-928-8K-cd1.mp4"
            existing_cd2 = folder / "SAVR-928-8K-cd2.mp4"

            source_file.touch()
            existing_cd1.touch()
            existing_cd2.touch()

            with patch("tools.rename.check_rename") as mock_check_rename:
                checkmp4(source_file.name, "SAVR-928-8K", str(source_file), str(folder))

            mock_check_rename.assert_called_once_with(
                str(source_file),
                str(folder / "SAVR-928-8K-cd3.mp4"),
            )


if __name__ == "__main__":
    unittest.main()
