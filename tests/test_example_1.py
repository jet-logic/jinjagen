import unittest
import tempfile
import subprocess
from pathlib import Path


class TestBackupScriptOutput(unittest.TestCase):
    def setUp(self):
        """Set up test files in a temp directory."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = Path(self.temp_dir.name)

        # Create template and config files
        (self.test_dir / "backup.sh.j2").write_text(
            r"""#!/bin/bash
BACKUP_PATHS=(#% for path in backup_paths %# "#{ path }#" #% endfor %#)
#% if notify.enabled %#
EMAIL="#{ notify.email }#"
#% endif %#"""
        )

        (self.test_dir / "test_config.json").write_text(
            r"""{
  "backup_paths": ["/test/path1", "/test/path2"],
  "notify": { "enabled": true, "email": "test@example.com" }
}"""
        )

    def tearDown(self):
        """Clean up temp directory."""
        self.temp_dir.cleanup()

    # @unittest.skip("Enable when needed")
    def test_generated_script_contains_paths_and_email(self):
        """Run jinjagen and verify the output script."""
        output_script = self.test_dir / "backup.sh"

        # Call jinjagen CLI to generate the script
        subprocess.run(
            [
                "python",
                "-m",
                "jinjagen",
                str(self.test_dir / "backup.sh.j2"),
                str(output_script),
                "-d",
                str(self.test_dir / "test_config.json"),
            ],
            check=True,
        )

        # Read the generated script
        generated_content = output_script.read_text()
        # print(output_script)
        # print(generated_content)

        # Verify expected content
        self.assertIn('BACKUP_PATHS=( "/test/path1"  "/test/path2" )', generated_content)
        self.assertIn('EMAIL="test@example.com"', generated_content)

    # @unittest.skip("Enable when needed")
    def test_email_omitted_when_disabled(self):
        """Test that EMAIL is omitted when notify.enabled=false."""
        # Override config
        (self.test_dir / "disabled_config.json").write_text(
            """{
  "backup_paths": ["/test/path1"],
  "notify": { "enabled": false }
}"""
        )

        output_script = self.test_dir / "backup_no_email.sh"
        subprocess.run(
            [
                "python",
                "-m",
                "jinjagen",
                str(self.test_dir / "backup.sh.j2"),
                str(output_script),
                "-d",
                str(self.test_dir / "disabled_config.json"),
            ],
            check=True,
        )

        generated_content = output_script.read_text()
        self.assertNotIn("EMAIL=", generated_content)


if __name__ == "__main__":
    unittest.main()
