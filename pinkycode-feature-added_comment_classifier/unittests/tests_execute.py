import unittest

from .test_metrics import TestDensityAssessment, TestReadabilityAssessment, TestCommentedPctAssessment
from .test_file_upload import TestNotZipUpload
from .test_agent import TestJSONFeedback
from .test_nltk import TestSyllablesCounting

if __name__ == "__main__":
    unittest.main()