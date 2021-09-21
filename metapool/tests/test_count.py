import os
import pandas as pd

from unittest import main, TestCase

from metapool import KLSampleSheet
from metapool.count import (_extract_name_and_lane, _parse_samtools_counts,
                            _parse_fastp_counts, bcl2fastq_counts,
                            fastp_counts, minimap2_counts, run_counts)


class TestCount(TestCase):
    def setUp(self):
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        self.run_dir = os.path.join(data_dir, 'runs',
                                    '200318_A00953_0082_AH5TWYDSXY')
        self.ss = KLSampleSheet(os.path.join(self.run_dir, 'sample-sheet.csv'))

        self.stats = pd.DataFrame(RUN_STATS)
        # help make comparisons consistent
        self.stats.sort_index(inplace=True)

        self.stats.index.set_names(['Sample_ID', 'Lane'], inplace=True)

    def test_extract_name_and_lane(self):
        self.assertEqual(
            _extract_name_and_lane('33333_G2750L_S2031_L001_I1_001.fastq.gz'),
                                  ('33333_G2750L', '1'))
        self.assertEqual(
            _extract_name_and_lane('33333_G2750L_S2031_L001_R1_001.fastq.gz'),
                                  ('33333_G2750L', '1'))
        self.assertEqual(
            _extract_name_and_lane('33333_G2750L_S2031_L001_R2_001.fastq.gz'),
                                  ('33333_G2750L', '1'))
        self.assertEqual(
            _extract_name_and_lane('33333_G2751R_S2072_L009_R1_001.fastq.gz'),
                                  ('33333_G2751R', '9'))
        self.assertEqual(
            _extract_name_and_lane('33333_G2751R_S2072_L010_R1_001.fastq.gz'),
                                  ('33333_G2751R', '10'))

    def test_extract_name_and_lane_terrible_pattern(self):
        # this is likely to never happen but we label a sample with the same
        # scheme that Illumina would use to identify differnt cells, lanes, and
        # orientations
        self.assertEqual(
            _extract_name_and_lane('S2031_L001_R1_S2031_L001_I1_001.fastq.gz'),
                                  ('S2031_L001_R1', '1'))

    def test_parse_fastp_counts(self):
        obs = _parse_fastp_counts(
            os.path.join(self.run_dir, 'Trojecp_666', 'json',
                         'sample3_S457_L003_R1_001.json'))

        self.assertEqual(obs, 4692)

    def test_parse_samtools_counts(self):
        obs = _parse_samtools_counts(
            os.path.join(self.run_dir, 'Trojecp_666', 'samtools',
                         'sample4_S369_L003_R1_001.log'))

        self.assertEqual(obs, 2777)

    def test_bcl2fastq_counts(self):
        obs = bcl2fastq_counts(self.run_dir, self.ss)
        pd.testing.assert_frame_equal(obs.sort_index(),
                                      self.stats[['bcl']])

    def test_fastp_counts(self):
        obs = fastp_counts(self.run_dir, self.ss)
        pd.testing.assert_frame_equal(obs.sort_index(),
                                      self.stats[['fastp']])

    def test_minimap2_counts(self):
        obs = minimap2_counts(self.run_dir, self.ss)
        pd.testing.assert_frame_equal(obs.sort_index(),
                                      self.stats[['minimap2']])

    def test_count_collector(self):
        obs = run_counts(self.run_dir, self.ss)
        pd.testing.assert_frame_equal(obs.sort_index(), self.stats)


RUN_STATS = {
    'bcl': {('sample1', '1'): 10000, ('sample2', '1'): 100000,
            ('sample1', '3'): 100000, ('sample2', '3'): 2300000,
            ('sample3', '3'): 300000, ('sample4', '3'): 400000,
            ('sample5', '3'): 567000},
    'fastp': {('sample1', '1'): 10800, ('sample2', '1'): 61404,
              ('sample1', '3'): 335996, ('sample2', '3'): 18374,
              ('sample3', '3'): 4692, ('sample4', '3'): 960,
              ('sample5', '3'): 30846196},
    'minimap2': {('sample1', '1'): 111172.0, ('sample2', '1'): 277611.0,
                 ('sample1', '3'): 1168275.0, ('sample2', '3'): 1277.0,
                 ('sample3', '3'): 33162.0, ('sample4', '3'): 2777.0,
                 ('sample5', '3'): 4337654.0}
}


if __name__ == '__main__':
    main()