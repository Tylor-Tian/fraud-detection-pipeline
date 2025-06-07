"""Performance tests for fraud detection system."""

import pytest
import time
from datetime import datetime
import concurrent.futures
from statistics import mean, stdev

from fraud_detection import FraudDetectionSystem
from fraud_detection.models import Transaction


@pytest.mark.performance
class TestPerformance:
    """Performance tests."""
    
    @pytest.fixture
    def detector(self, temp_model_file):
        """Create detector for performance testing."""
        return FraudDetectionSystem(
            redis_host="localhost",
            model_path=temp_model_file
        )
    
    def test_single_transaction_performance(self, detector):
        """Test single transaction processing time."""
        transaction = Transaction(
            transaction_id="PERF_TEST_001",
            user_id="PERF_USER",
            amount=100.0,
            merchant_id="PERF_MERCHANT",
            timestamp=datetime.now()
        )
        
        # Warm up
        detector.process_transaction(transaction)
        
        # Measure processing time
        times = []
        for i in range(100):
            transaction.transaction_id = f"PERF_TEST_{i}"
            
            start_time = time.time()
            result = detector.process_transaction(transaction)
            end_time = time.time()
            
            processing_time = (end_time - start_time) * 1000  # Convert to ms
            times.append(processing_time)
        
        avg_time = mean(times)
        std_time = stdev(times)
        
        # Performance assertions
        assert avg_time < 100  # Average under 100ms
        assert max(times) < 200  # No transaction over 200ms
        
        print(f"\nPerformance Results:")
        print(f"Average: {avg_time:.2f}ms")
        print(f"Std Dev: {std_time:.2f}ms")
        print(f"Min: {min(times):.2f}ms")
        print(f"Max: {max(times):.2f}ms")
    
    def test_concurrent_processing(self, detector):
        """Test concurrent transaction processing."""
        def process_transaction(i):
            transaction = Transaction(
                transaction_id=f"CONCURRENT_{i}",
                user_id=f"USER_{i % 10}",
                amount=100.0 + (i % 100),
                merchant_id=f"MERCHANT_{i % 5}",
                timestamp=datetime.now()
            )
            
            start_time = time.time()
            result = detector.process_transaction(transaction)
            end_time = time.time()
            
            return (end_time - start_time) * 1000, result
        
        # Process transactions concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            start_time = time.time()
            futures = [executor.submit(process_transaction, i) for i in range(100)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
            end_time = time.time()
        
        total_time = (end_time - start_time) * 1000
        processing_times = [r[0] for r in results]
        
        print(f"\nConcurrent Processing Results:")
        print(f"Total time for 100 transactions: {total_time:.2f}ms")
        print(f"Throughput: {100 / (total_time / 1000):.2f} TPS")
        print(f"Average processing time: {mean(processing_times):.2f}ms")
        
        # Assertions
        assert total_time < 5000  # 100 transactions in under 5 seconds
        assert all(r[1].transaction_id.startswith("CONCURRENT_") for r in results)
        
