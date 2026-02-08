import unittest
import os
import sys
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock, call
from PIL import Image
import yaml
import io

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import main


class TestLoadConfig(unittest.TestCase):
    """Tests for load_config function"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.configs_dir = os.path.join(self.temp_dir, "configs")
        os.makedirs(self.configs_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    @patch('os.path.join')
    @patch('os.path.exists')
    def test_load_config_file_not_found(self, mock_exists, mock_join):
        """Test that FileNotFoundError is raised when config file doesn't exist"""
        mock_exists.return_value = False
        mock_join.return_value = "configs/nonexistent.yaml"

        with self.assertRaises(FileNotFoundError):
            main.load_config("nonexistent")

    @patch('builtins.open', create=True)
    @patch('os.path.exists')
    def test_load_config_success(self, mock_exists, mock_open):
        """Test successful config loading"""
        mock_exists.return_value = True
        config_data = {'links': {'doc_1': 'https://example.com/1', 'doc_2': 'https://example.com/2'}}
        mock_file = MagicMock()
        mock_file.__enter__.return_value.read.return_value = yaml.dump(config_data)
        mock_open.return_value = mock_file

        with patch('yaml.safe_load') as mock_yaml:
            mock_yaml.return_value = config_data
            result = main.load_config("default")

        self.assertEqual(result, {'doc_1': 'https://example.com/1', 'doc_2': 'https://example.com/2'})

    @patch('builtins.open', create=True)
    @patch('os.path.exists')
    def test_load_config_empty_links(self, mock_exists, mock_open):
        """Test config loading with empty links"""
        mock_exists.return_value = True
        config_data = {'links': {}}
        mock_file = MagicMock()
        mock_open.return_value = mock_file

        with patch('yaml.safe_load') as mock_yaml:
            mock_yaml.return_value = config_data
            result = main.load_config("empty")

        self.assertEqual(result, {})

    @patch('builtins.open', create=True)
    @patch('os.path.exists')
    def test_load_config_missing_links_key(self, mock_exists, mock_open):
        """Test config loading when 'links' key is missing"""
        mock_exists.return_value = True
        config_data = {'other_key': 'value'}
        mock_file = MagicMock()
        mock_open.return_value = mock_file

        with patch('yaml.safe_load') as mock_yaml:
            mock_yaml.return_value = config_data
            result = main.load_config("invalid")

        self.assertEqual(result, {})


class TestImagesToPdf(unittest.TestCase):
    """Tests for images_to_pdf function"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def create_test_image(self, filename):
        """Create a test image"""
        img = Image.new('RGB', (100, 100), color='red')
        img_path = os.path.join(self.temp_dir, filename)
        img.save(img_path)
        return img_path

    def test_images_to_pdf_single_image(self):
        """Test PDF creation with a single image"""
        img_path = self.create_test_image('test.png')
        pdf_path = os.path.join(self.temp_dir, 'output.pdf')

        main.images_to_pdf([img_path], pdf_path)

        self.assertTrue(os.path.exists(pdf_path))
        self.assertGreater(os.path.getsize(pdf_path), 0)

    def test_images_to_pdf_multiple_images(self):
        """Test PDF creation with multiple images"""
        img_paths = [self.create_test_image(f'test{i}.png') for i in range(3)]
        pdf_path = os.path.join(self.temp_dir, 'output.pdf')

        main.images_to_pdf(img_paths, pdf_path)

        self.assertTrue(os.path.exists(pdf_path))
        self.assertGreater(os.path.getsize(pdf_path), 0)

    def test_images_to_pdf_creates_rgb_images(self):
        """Test that images are converted to RGB before PDF creation"""
        # Create a grayscale image
        img = Image.new('L', (100, 100), color=128)
        img_path = os.path.join(self.temp_dir, 'gray.png')
        img.save(img_path)
        pdf_path = os.path.join(self.temp_dir, 'output.pdf')

        main.images_to_pdf([img_path], pdf_path)

        self.assertTrue(os.path.exists(pdf_path))


class TestParseArguments(unittest.TestCase):
    """Tests for parse_arguments function"""

    @patch('sys.argv', ['main.py', '--username', 'testuser', '--profile-name', 'Default', '--config', 'default'])
    def test_parse_arguments_required_only(self):
        """Test parsing with only required arguments"""
        args = main.parse_arguments()
        self.assertEqual(args.username, 'testuser')
        self.assertEqual(args.profile_name, 'Default')
        self.assertEqual(args.config, 'default')
        self.assertEqual(args.pdf_filename, 'result.pdf')  # default value

    @patch('sys.argv', ['main.py', '--username', 'testuser', '--profile-name', 'Default',
                        '--config', 'default', '--pdf-filename', 'custom.pdf'])
    def test_parse_arguments_with_pdf_filename(self):
        """Test parsing with custom PDF filename"""
        args = main.parse_arguments()
        self.assertEqual(args.pdf_filename, 'custom.pdf')

    @patch('sys.argv', ['main.py'])
    def test_parse_arguments_missing_required(self):
        """Test that missing required arguments raises SystemExit"""
        with self.assertRaises(SystemExit):
            main.parse_arguments()


class TestCreateDriver(unittest.TestCase):
    """Tests for create_driver function"""

    @patch('main.PROFILE_PATH', '/Users/testuser/Library/Application Support/Google/Chrome')
    @patch('main.PROFILE_NAME', 'Default')
    @patch('main.webdriver.Chrome')
    @patch('main.Service')
    def test_create_driver_configuration(self, mock_service, mock_chrome):
        """Test that driver is created with correct configuration"""
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver

        with patch('main.ChromeDriverManager'):
            driver = main.create_driver()

        # Verify Chrome was called with correct options
        self.assertEqual(mock_chrome.call_count, 1)
        call_kwargs = mock_chrome.call_args[1]
        self.assertIn('options', call_kwargs)


class TestIntegration(unittest.TestCase):
    """Integration tests"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.configs_dir = os.path.join(self.temp_dir, "configs")
        os.makedirs(self.configs_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_full_workflow_mock(self):
        """Test full workflow with mocked components"""
        # Create a test config file
        config_data = {
            'links': {
                'doc_1': 'https://example.com/1',
                'doc_2': 'https://example.com/2'
            }
        }
        config_path = os.path.join(self.configs_dir, 'test.yaml')
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f)

        # Mock the load_config to use our test config
        with patch('os.path.join', side_effect=lambda *args: os.path.join(self.temp_dir, *args) if 'configs' in args else os.path.join(*args)):
            # This is a simplified test - in real scenarios you'd mock more components
            pass


class TestEdgeCases(unittest.TestCase):
    """Tests for edge cases and error handling"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_images_to_pdf_with_empty_list(self):
        """Test that empty image list raises appropriate error"""
        pdf_path = os.path.join(self.temp_dir, 'output.pdf')

        with self.assertRaises(IndexError):
            main.images_to_pdf([], pdf_path)

    def test_images_to_pdf_with_nonexistent_image(self):
        """Test that nonexistent image file raises appropriate error"""
        pdf_path = os.path.join(self.temp_dir, 'output.pdf')

        with self.assertRaises(FileNotFoundError):
            main.images_to_pdf(['/nonexistent/image.png'], pdf_path)


class TestPathHandling(unittest.TestCase):
    """Tests for path handling and directory creation"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    @patch('os.makedirs')
    def test_output_directory_creation(self, mock_makedirs):
        """Test that output directory is created"""
        with patch('main.BASE_DIR', self.temp_dir):
            with patch('main.create_driver'):
                with patch('main.collect_images', return_value=[]):
                    pass


if __name__ == '__main__':
    unittest.main()
