import unittest
from unittest.mock import patch, Mock
from cidr_allocation import allocate_subnets_for_config, allocate_cidrs_from_pool

class TestAWSOperations(unittest.TestCase):

   
    def setUp(self):
        self.scenarios = {
            "scenario_1": {
                "all_cidrs": ["10.0.0.0/16", "10.1.0.0/16"],
                "config": [{"prefixlen": 24}],
                "expected": ["10.0.0.0/24"]
            },
            "scenario_2": {
                "all_cidrs": ["10.0.0.0/16"],
                "config": [{"prefixlen": 24}, {"prefixlen": 25}],
                "expected": ["10.0.0.0/24", "10.0.1.0/25"]
            },
            "scenario_3": {
                "all_cidrs": ["10.0.0.0/16", "10.1.0.0/16"],
                "config": [{"prefixlen": 25, "cidr_pointer": 1}],
                "expected": ["10.1.0.0/25"]
            },
            "scenario_4": {
                "all_cidrs": ["10.0.0.0/16", "10.1.0.0/16"],
                "config": [{"prefixlen": 25, "cidr_pointer": 1}],
                "expected": ["10.1.0.0/25"]
            },
            "scenario_5": {
                "all_cidrs": ["10.0.0.0/16", "10.1.0.0/16"],
                "config": [{"prefixlen": 25}],
                "expected": ["10.0.0.0/25"]
            },
            "scenario_6": {
                "all_cidrs": ["10.0.0.0/16", "10.1.0.0/16"],
                "config": [{"prefixlen": 25, "cidr_pointer": 1}],
                "expected": ["10.1.0.0/25"]
            }
        }

    def test_allocate_subnets_for_config_1(self):
        scenario = self.scenarios["scenario_1"]
        result = allocate_subnets_for_config(scenario["all_cidrs"], scenario["config"])
        self.assertEqual(result, scenario["expected"])

    def test_allocate_subnets_for_config_2(self):
        scenario = self.scenarios["scenario_2"]
        result = allocate_subnets_for_config(scenario["all_cidrs"], scenario["config"])
        self.assertEqual(result, scenario["expected"])

    def test_allocate_subnets_for_config_3(self):
        scenario = self.scenarios["scenario_3"]
        result = allocate_subnets_for_config(scenario["all_cidrs"], scenario["config"])
        self.assertEqual(result, scenario["expected"])

    def test_allocate_subnets_for_config_4(self):
        scenario = self.scenarios["scenario_4"]
        result = allocate_subnets_for_config(scenario["all_cidrs"], scenario["config"])
        self.assertEqual(result, scenario["expected"])

    def test_allocate_subnets_for_config_5(self):
        scenario = self.scenarios["scenario_5"]
        result = allocate_subnets_for_config(scenario["all_cidrs"], scenario["config"])
        self.assertEqual(result, scenario["expected"])

    def test_allocate_subnets_for_config_6(self):
        scenario = self.scenarios["scenario_6"]
        result = allocate_subnets_for_config(scenario["all_cidrs"], scenario["config"])
        self.assertEqual(result, scenario["expected"])
  
    mock_response = {
        'IpamPoolAllocation': {
            'Cidr': '10.0.0.0/24'
        }
    }

    @patch('cidr_allocation.boto3')
    def test_allocate_cidrs_from_pool_1(self, mock_boto3):
        mock_client = Mock()
        mock_boto3.client.return_value = mock_client
        mock_client.allocate_ipam_pool_cidr.return_value = self.mock_response
        
        ipam_pool_id = "test_pool_id"
        prefix_lengths = [24]
        description = "test_description"
        result = allocate_cidrs_from_pool(ipam_pool_id, prefix_lengths, description)
        
        self.assertEqual(result, ["10.0.0.0/24"])


if __name__ == '__main__':
    unittest.main()
