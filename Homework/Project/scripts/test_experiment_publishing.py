from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

import export_two_pass
import watch_two_pass
from two_pass import metadata


class PublishingGuards(unittest.TestCase):
    def test_export_whitelists_metadata_and_handles_partial_prediction(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            out=root/'artifacts';dest=root/'reports';(out/'model').mkdir(parents=True)
            metadata(out/'job.json',{'status':'running','current_stage':'model','secret':'must-not-export'})
            metadata(out/'model/run.json',{'status':'running','unknown_secret':'must-not-export',
                'spec':{'input_sha256':'abc','secret':'must-not-export'}})
            (out/'model/predictions.jsonl').write_text('{"status":"predicted"}\n{"unfinished"',encoding='utf-8')
            with patch.object(export_two_pass,'OUT',out),patch.object(export_two_pass,'DEST',dest):
                state=export_two_pass.export()
            self.assertEqual(state['runs']['model']['records_written'],1)
            self.assertNotIn('must-not-export',(dest/'latest.json').read_text())

    def test_publisher_refuses_unrelated_staged_files(self):
        with patch.object(watch_two_pass,'git',return_value=SimpleNamespace(returncode=0,stdout='other.txt\n')) as git:
            with self.assertRaisesRegex(RuntimeError,'unrelated'):
                watch_two_pass.publish()
            self.assertEqual(git.call_count,1)


if __name__=='__main__':unittest.main()
