#!/usr/bin/env python3
"""Build rootless Home-rule carrier apply and restore templates OFFLINE.

Nothing in this script accesses the television. Requires a privately stored,
read-only original stock key-rule report so mismatched models fail closed.
Packages are unsigned. Do not install before recovery is tested.
"""
import argparse
import json
import pathlib
import re
import struct
import subprocess
import xml.etree.ElementTree as ET
import zipfile
import zlib

NAMESPACE = 'http://tizen.org/ns/packages'
SAMSUNG = 'com.samsung.tv.csfs'
PACKAGE = 'TvHmKey001'
APP = PACKAGE + '.Rule'
DEFAULT_TARGET = 'HdmiHome01.Launcher'
EXPECTED = [SAMSUNG, 'XF86Home', None, None, '~system:product:lfd',
            'launch', 'package:' + SAMSUNG, 'entry_point:smarthub_key']
ROOT = pathlib.Path(__file__).resolve().parents[1]


def validate_baseline(data):
    """Require one exact stock Home rule; never guess from a similar model."""
    try:
        rows = data['tables']['key_filter']
        matches = [row[1:] for row in rows if len(row) == 9
                   and row[1] == SAMSUNG and row[2] == 'XF86Home']
        managed = [row[1:] for row in data['tables']['managed_app']
                   if len(row) == 4 and row[1] == SAMSUNG]
    except (KeyError, TypeError) as exc:
        raise ValueError('Missing key_filter/managed_app baseline') from exc
    if matches != [EXPECTED] or managed != [[SAMSUNG, 'partial', None]]:
        raise ValueError('Stock Home baseline differs. STOP: do not install.')


def icon_png():
    def chunk(typ, data):
        return struct.pack('>I', len(data)) + typ + data + struct.pack('>I', zlib.crc32(typ + data) & 0xffffffff)
    pixels = b''.join(b'\x00' + b'\x2b\x4e\x68\xff' * 32 for _ in range(32))
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', 32, 32, 8, 6, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(pixels)) + chunk(b'IEND', b''))


def make_manifest(target, version, restore=False):
    if not re.fullmatch(r'[A-Za-z0-9]{10}\.[A-Za-z0-9_]+', target):
        raise ValueError('Target must be a valid Tizen app ID, e.g. HdmiHome01.Launcher')
    if target == SAMSUNG:
        raise ValueError('Use --restore to restore stock, not --target')
    if not re.fullmatch(r'\d+\.\d+\.\d+', version):
        raise ValueError('Invalid semantic version')
    ET.register_namespace('', NAMESPACE)
    el = lambda name: '{' + NAMESPACE + '}' + name
    manifest = ET.Element(el('manifest'), {'api-version': '4.0', 'package': PACKAGE, 'version': version})
    ET.SubElement(manifest, el('profile'), {'name': 'common'})
    app = ET.SubElement(manifest, el('ui-application'), {
        'appid': APP, 'exec': 'homekey-stub', 'type': 'capp',
        'multiple': 'false', 'taskmanage': 'false', 'nodisplay': 'true'})
    ET.SubElement(app, el('label')).text = 'HDMI Home Rule Carrier'
    ET.SubElement(app, el('icon')).text = 'homekey.png'
    context = ET.SubElement(manifest, el('app-context'), {'appid': SAMSUNG, 'ui-type': 'partial'})
    rule = ET.SubElement(context, el('app-context-rule'))
    ET.SubElement(rule, el('source'), {'selector': 'key'}).text = 'XF86Home'
    ET.SubElement(rule, el('condition'), {'selector': 'product', 'operator': 'not'}).text = 'lfd'
    ET.SubElement(rule, el('target'), {
        'selector': 'app', 'request': 'launch',
        'args': 'entry_point:smarthub_key' if restore else 'entry_point:home'
    }).text = SAMSUNG if restore else target
    ET.SubElement(manifest, el('shortcut-list'))
    privileges = ET.SubElement(manifest, el('privileges'))
    ET.SubElement(privileges, el('privilege')).text = 'http://tizen.org/privilege/appmanager.launch'
    ET.indent(manifest)
    return ET.tostring(manifest, encoding='utf-8', xml_declaration=True)


def compile_stub(output):
    subprocess.run(['arm-linux-gnueabi-gcc', '-march=armv7-a', '-marm', '-nostdlib',
                    '-static', '-Os', '-fno-stack-protector', '-fno-unwind-tables',
                    '-fno-asynchronous-unwind-tables', '-Wl,-e,_start',
                    '-Wl,--build-id=none', '-Wl,-z,noexecstack',
                    str(ROOT / 'native/exit-only.c'), '-o', str(output)], check=True)
    output.chmod(0o755)


def package_manifest(outdir, manifest, filename, manifest_only=False):
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / 'tizen-manifest.xml').write_bytes(manifest)
    if manifest_only:
        return
    stage = outdir / 'stage'
    (stage / 'bin').mkdir(parents=True, exist_ok=True)
    (stage / 'shared/res').mkdir(parents=True, exist_ok=True)
    (stage / 'tizen-manifest.xml').write_bytes(manifest)
    (stage / 'shared/res/homekey.png').write_bytes(icon_png())
    compile_stub(stage / 'bin/homekey-stub')
    with zipfile.ZipFile(outdir / filename, 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(stage.rglob('*')):
            if path.is_file():
                archive.write(path, path.relative_to(stage).as_posix())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=pathlib.Path, required=True,
                        help='Private read-only original stock report (never commit)')
    parser.add_argument('--out', type=pathlib.Path, default=pathlib.Path('dist'))
    parser.add_argument('--target', default=DEFAULT_TARGET)
    parser.add_argument('--apply-version', default='0.1.0')
    parser.add_argument('--restore-version', default='0.1.1')
    parser.add_argument('--manifest-only', action='store_true',
                        help='Validate and render XML without cross compiler')
    args = parser.parse_args()
    validate_baseline(json.loads(args.baseline.read_text()))
    if tuple(map(int, args.restore_version.split('.'))) <= tuple(map(int, args.apply_version.split('.'))):
        parser.error('Restore version must be greater than apply version')
    if args.out.resolve() == ROOT.resolve():
        parser.error('Output must not be project root')
    for name, version, restore in [('apply', args.apply_version, False),
                                    ('restore', args.restore_version, True)]:
        data = make_manifest(args.target, version, restore)
        package_manifest(args.out / name, data, 'home-route-' + name + '.tpk', args.manifest_only)
    print('Prepared OFFLINE artifacts in', args.out, '(unsigned; no TV access).')
    print('IMPORTANT: sign and verify restore first. Never uninstall active carrier before restore.')


if __name__ == '__main__':
    main()
