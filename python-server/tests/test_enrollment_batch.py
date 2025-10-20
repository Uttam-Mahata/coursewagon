# tests/test_enrollment_batch.py
"""
Test batch enrollment checking functionality
"""
import pytest
from unittest.mock import Mock, MagicMock
from services.enrollment_service import EnrollmentService
from repositories.enrollment_repository import EnrollmentRepository
from models.enrollment import Enrollment


def test_check_enrollments_batch_all_enrolled():
    """Test batch enrollment check when user is enrolled in all courses"""
    # Mock database session
    mock_db = Mock()
    
    # Create mock enrollments
    enrollment1 = Mock(spec=Enrollment)
    enrollment1.course_id = 1
    enrollment1.to_dict.return_value = {'id': 1, 'course_id': 1, 'user_id': 1}
    
    enrollment2 = Mock(spec=Enrollment)
    enrollment2.course_id = 2
    enrollment2.to_dict.return_value = {'id': 2, 'course_id': 2, 'user_id': 1}
    
    # Mock repository
    mock_repo = Mock(spec=EnrollmentRepository)
    mock_repo.get_enrollments_batch.return_value = [enrollment1, enrollment2]
    
    # Create service and inject mock repo
    service = EnrollmentService(mock_db)
    service.enrollment_repo = mock_repo
    
    # Test batch check
    result = service.check_enrollments_batch(1, [1, 2])
    
    # Verify results
    assert '1' in result
    assert '2' in result
    assert result['1']['enrolled'] is True
    assert result['2']['enrolled'] is True
    assert result['1']['enrollment'] == {'id': 1, 'course_id': 1, 'user_id': 1}
    assert result['2']['enrollment'] == {'id': 2, 'course_id': 2, 'user_id': 1}


def test_check_enrollments_batch_partially_enrolled():
    """Test batch enrollment check when user is enrolled in some courses"""
    # Mock database session
    mock_db = Mock()
    
    # Create mock enrollment for only course 1
    enrollment1 = Mock(spec=Enrollment)
    enrollment1.course_id = 1
    enrollment1.to_dict.return_value = {'id': 1, 'course_id': 1, 'user_id': 1}
    
    # Mock repository - only return enrollment for course 1
    mock_repo = Mock(spec=EnrollmentRepository)
    mock_repo.get_enrollments_batch.return_value = [enrollment1]
    
    # Create service and inject mock repo
    service = EnrollmentService(mock_db)
    service.enrollment_repo = mock_repo
    
    # Test batch check for courses 1, 2, 3
    result = service.check_enrollments_batch(1, [1, 2, 3])
    
    # Verify results
    assert '1' in result
    assert '2' in result
    assert '3' in result
    assert result['1']['enrolled'] is True
    assert result['2']['enrolled'] is False
    assert result['3']['enrolled'] is False
    assert result['1']['enrollment'] is not None
    assert result['2']['enrollment'] is None
    assert result['3']['enrollment'] is None


def test_check_enrollments_batch_none_enrolled():
    """Test batch enrollment check when user is not enrolled in any courses"""
    # Mock database session
    mock_db = Mock()
    
    # Mock repository - return empty list
    mock_repo = Mock(spec=EnrollmentRepository)
    mock_repo.get_enrollments_batch.return_value = []
    
    # Create service and inject mock repo
    service = EnrollmentService(mock_db)
    service.enrollment_repo = mock_repo
    
    # Test batch check
    result = service.check_enrollments_batch(1, [1, 2, 3])
    
    # Verify results
    assert '1' in result
    assert '2' in result
    assert '3' in result
    assert result['1']['enrolled'] is False
    assert result['2']['enrolled'] is False
    assert result['3']['enrolled'] is False
    assert result['1']['enrollment'] is None
    assert result['2']['enrollment'] is None
    assert result['3']['enrollment'] is None


def test_check_enrollments_batch_empty_list():
    """Test batch enrollment check with empty course list"""
    # Mock database session
    mock_db = Mock()
    
    # Mock repository
    mock_repo = Mock(spec=EnrollmentRepository)
    mock_repo.get_enrollments_batch.return_value = []
    
    # Create service and inject mock repo
    service = EnrollmentService(mock_db)
    service.enrollment_repo = mock_repo
    
    # Test batch check with empty list
    result = service.check_enrollments_batch(1, [])
    
    # Verify results
    assert result == {}
