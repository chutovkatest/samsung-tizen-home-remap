import importlib.util
import pathlib
import unittest
import xml.etree.ElementTree as ET

PATH = pathlib.Path(__file__).resolve().parents[1] / 'tools/build.py'
spec = importlib.util.spec_from_file_location('home_builder', PATH)
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


def sample():
    return {'tables': {'key_filter': [[1] + builder.EXPECTED],
                       'managed_app': [[1, builder.SAMSUNG, 'partial', None]]}}


class OfflineTests(unittest.TestCase):
    def test_stock_baseline_passes(self):
        builder.validate_baseline(sample())

    def test_mismatch_fails_closed(self):
        data = sample()
        data['tables']['key_filter'][0][-1] = 'entry_point:unexpected'
        with self.assertRaises(ValueError):
            builder.validate_baseline(data)

    def test_duplicate_rule_fails_closed(self):
        data = sample()
        data['tables']['key_filter'].append([2] + builder.EXPECTED)
        with self.assertRaises(ValueError):
            builder.validate_baseline(data)

    def test_manifest_apply_and_restore(self):
        el = lambda x: '{' + builder.NAMESPACE + '}' + x
        for restore, expected_target, expected_args in [
            (False, 'HdmiHome01.Launcher', 'entry_point:home'),
            (True, builder.SAMSUNG, 'entry_point:smarthub_key')
        ]:
            root = ET.fromstring(builder.make_manifest('HdmiHome01.Launcher', '0.1.0', restore))
            context = root.find(el('app-context'))
            self.assertEqual(context.attrib['appid'], builder.SAMSUNG)
            dest = context.find(el('app-context-rule')).find(el('target'))
            self.assertEqual(dest.text, expected_target)
            self.assertEqual(dest.attrib['args'], expected_args)

    def test_app_id_validation(self):
        with self.assertRaises(ValueError):
            builder.make_manifest('private.local/launcher', '0.1.0')


if __name__ == '__main__':
    unittest.main()
