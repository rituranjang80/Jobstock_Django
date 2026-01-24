"""
Generic Base Service Layer - Production Ready
Provides reusable CRUD operations for all models
Supports both Django Templates (MVT) and REST API
Author: Reetch Development Team
Date: December 22, 2025
"""
from typing import Dict, Any, Optional, List, Type, Union
from django.db import models, transaction
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, QuerySet, Count, Avg, Sum
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class ServiceResponse:
    """Standardized response format for both MVT and API"""
    
    @staticmethod
    def success(data: Any = None, message: str = "Operation successful", **kwargs) -> Dict[str, Any]:
        """Success response"""
        return {
            'success': True,
            'message': message,
            'data': data,
            'error': None,
            'timestamp': timezone.now().isoformat(),
            **kwargs
        }
    
    @staticmethod
    def error(message: str, errors: Any = None, code: str = 'ERROR', **kwargs) -> Dict[str, Any]:
        """Error response"""
        return {
            'success': False,
            'message': message,
            'data': None,
            'error': errors,
            'error_code': code,
            'timestamp': timezone.now().isoformat(),
            **kwargs
        }
    
    @staticmethod
    def paginated(data: List, page: int, per_page: int, total: int, **kwargs) -> Dict[str, Any]:
        """Paginated response"""
        total_pages = (total + per_page - 1) // per_page
        return {
            'success': True,
            'data': data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1
            },
            'timestamp': timezone.now().isoformat(),
            **kwargs
        }


class GenericService:
    """
    Generic service class with comprehensive CRUD operations
    Can be used standalone or inherited by specific services
    
    Example Usage:
        # Direct usage
        job_service = GenericService(Job)
        result = job_service.create({'title': 'Developer'})
        
        # Inherited usage
        class JobService(GenericService):
            model = Job
    """
    
    model: Type[models.Model] = None  # Override in child classes
    
    def __init__(self, model: Optional[Type[models.Model]] = None):
        """Initialize service with model"""
        if model:
            self.model = model
        if not self.model:
            raise ValueError("Model must be specified either in class definition or constructor")
    
    # ==================== CREATE OPERATIONS ====================
    
    def create(self, data: Dict[str, Any], user: Optional[Any] = None, 
               auto_fields: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a new record
        
        Args:
            data: Dictionary of field values
            user: User performing the action (optional)
            auto_fields: Additional fields to auto-populate (e.g., created_by)
            
        Returns:
            ServiceResponse with created object
        """
        try:
            with transaction.atomic():
                # Prepare data
                clean_data = self._prepare_data(data)
                
                # Add auto fields
                if auto_fields:
                    clean_data.update(auto_fields)
                
                # Add user tracking if model has these fields
                if user:
                    if hasattr(self.model, 'created_by'):
                        clean_data['created_by'] = user
                    if hasattr(self.model, 'posted_by'):
                        clean_data['posted_by'] = user
                
                # Create instance
                instance = self.model(**clean_data)
                
                # Validate
                instance.full_clean()
                
                # Save
                instance.save()
                
                logger.info(f"Created {self.model.__name__} with ID {instance.pk}")
                
                return ServiceResponse.success(
                    data=self._serialize_instance(instance),
                    message=f"{self.model.__name__} created successfully"
                )
                
        except ValidationError as e:
            logger.warning(f"Validation error creating {self.model.__name__}: {e}")
            return ServiceResponse.error(
                message="Validation failed",
                errors=e.message_dict if hasattr(e, 'message_dict') else str(e),
                code='VALIDATION_ERROR'
            )
        except Exception as e:
            logger.error(f"Error creating {self.model.__name__}: {e}", exc_info=True)
            return ServiceResponse.error(
                message=f"Failed to create {self.model.__name__}",
                errors=str(e),
                code='CREATE_ERROR'
            )
    
    def bulk_create(self, data_list: List[Dict[str, Any]], 
                    batch_size: int = 100) -> Dict[str, Any]:
        """
        Create multiple records in bulk
        
        Args:
            data_list: List of dictionaries with field values
            batch_size: Number of records to create per batch
            
        Returns:
            ServiceResponse with created count
        """
        try:
            with transaction.atomic():
                instances = []
                for data in data_list:
                    clean_data = self._prepare_data(data)
                    instances.append(self.model(**clean_data))
                
                created = self.model.objects.bulk_create(instances, batch_size=batch_size)
                
                logger.info(f"Bulk created {len(created)} {self.model.__name__} records")
                
                return ServiceResponse.success(
                    data={'count': len(created), 'ids': [obj.pk for obj in created]},
                    message=f"{len(created)} records created successfully"
                )
                
        except Exception as e:
            logger.error(f"Error in bulk create: {e}", exc_info=True)
            return ServiceResponse.error(
                message="Bulk create failed",
                errors=str(e),
                code='BULK_CREATE_ERROR'
            )
    
    # ==================== READ OPERATIONS ====================
    
    def get_by_id(self, pk: int, select_related: Optional[List[str]] = None,
                  prefetch_related: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get a single record by primary key
        
        Args:
            pk: Primary key value
            select_related: Fields to select_related
            prefetch_related: Fields to prefetch_related
            
        Returns:
            ServiceResponse with object data
        """
        try:
            queryset = self.model.objects.all()
            
            if select_related:
                queryset = queryset.select_related(*select_related)
            if prefetch_related:
                queryset = queryset.prefetch_related(*prefetch_related)
            
            instance = get_object_or_404(queryset, pk=pk)
            
            return ServiceResponse.success(
                data=self._serialize_instance(instance, include_relations=True),
                message=f"{self.model.__name__} retrieved successfully"
            )
            
        except Exception as e:
            logger.error(f"Error getting {self.model.__name__} with ID {pk}: {e}")
            return ServiceResponse.error(
                message=f"{self.model.__name__} not found",
                errors=str(e),
                code='NOT_FOUND'
            )
    
    def get_all(self, filters: Optional[Dict[str, Any]] = None,
                exclude: Optional[Dict[str, Any]] = None,
                order_by: Optional[List[str]] = None,
                select_related: Optional[List[str]] = None,
                prefetch_related: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get all records with optional filtering
        
        Args:
            filters: Q object filters or dict filters
            exclude: Fields to exclude
            order_by: List of fields to order by
            select_related: Fields to select_related
            prefetch_related: Fields to prefetch_related
            
        Returns:
            ServiceResponse with list of objects
        """
        try:
            queryset = self.model.objects.all()
            
            # Apply filters
            if filters:
                queryset = queryset.filter(**filters)
            
            if exclude:
                queryset = queryset.exclude(**exclude)
            
            # Optimize queries
            if select_related:
                queryset = queryset.select_related(*select_related)
            if prefetch_related:
                queryset = queryset.prefetch_related(*prefetch_related)
            
            # Order
            if order_by:
                queryset = queryset.order_by(*order_by)
            elif hasattr(self.model, '_meta') and self.model._meta.ordering:
                pass  # Use model's default ordering
            else:
                queryset = queryset.order_by('-id')
            
            data = [self._serialize_instance(obj) for obj in queryset]
            
            return ServiceResponse.success(
                data={'items': data, 'count': len(data)},
                message=f"Retrieved {len(data)} {self.model.__name__} records"
            )
            
        except Exception as e:
            logger.error(f"Error getting all {self.model.__name__}: {e}", exc_info=True)
            return ServiceResponse.error(
                message="Failed to retrieve records",
                errors=str(e),
                code='RETRIEVAL_ERROR'
            )
    
    def get_paginated(self, page: int = 1, per_page: int = 20,
                     filters: Optional[Dict[str, Any]] = None,
                     search: Optional[str] = None,
                     search_fields: Optional[List[str]] = None,
                     order_by: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get paginated records with search and filter
        
        Args:
            page: Page number (1-indexed)
            per_page: Items per page
            filters: Filter criteria
            search: Search query string
            search_fields: Fields to search in
            order_by: Fields to order by
            
        Returns:
            ServiceResponse with paginated data
        """
        try:
            queryset = self.model.objects.all()
            
            # Apply filters
            if filters:
                queryset = queryset.filter(**filters)
            
            # Apply search
            if search and search_fields:
                search_q = Q()
                for field in search_fields:
                    search_q |= Q(**{f"{field}__icontains": search})
                queryset = queryset.filter(search_q)
            
            # Order
            if order_by:
                queryset = queryset.order_by(*order_by)
            
            # Paginate
            paginator = Paginator(queryset, per_page)
            
            try:
                page_obj = paginator.page(page)
            except PageNotAnInteger:
                page_obj = paginator.page(1)
            except EmptyPage:
                page_obj = paginator.page(paginator.num_pages)
            
            data = [self._serialize_instance(obj) for obj in page_obj.object_list]
            
            return ServiceResponse.paginated(
                data=data,
                page=page_obj.number,
                per_page=per_page,
                total=paginator.count,
                message=f"Page {page_obj.number} of {paginator.num_pages}"
            )
            
        except Exception as e:
            logger.error(f"Error in pagination: {e}", exc_info=True)
            return ServiceResponse.error(
                message="Pagination failed",
                errors=str(e),
                code='PAGINATION_ERROR'
            )
    
    # ==================== UPDATE OPERATIONS ====================
    
    def update(self, pk: int, data: Dict[str, Any], 
               user: Optional[Any] = None, partial: bool = True) -> Dict[str, Any]:
        """
        Update a record
        
        Args:
            pk: Primary key value
            data: Dictionary of fields to update
            user: User performing the action
            partial: Allow partial updates
            
        Returns:
            ServiceResponse with updated object
        """
        try:
            with transaction.atomic():
                instance = get_object_or_404(self.model, pk=pk)
                
                # Prepare update data
                clean_data = self._prepare_data(data, partial=partial)
                
                # Add user tracking
                if user and hasattr(self.model, 'updated_by'):
                    clean_data['updated_by'] = user
                
                # Update fields
                for field, value in clean_data.items():
                    setattr(instance, field, value)
                
                # Validate
                instance.full_clean()
                
                # Save
                instance.save()
                
                logger.info(f"Updated {self.model.__name__} ID {pk}")
                
                return ServiceResponse.success(
                    data=self._serialize_instance(instance),
                    message=f"{self.model.__name__} updated successfully"
                )
                
        except ObjectDoesNotExist:
            return ServiceResponse.error(
                message=f"{self.model.__name__} not found",
                code='NOT_FOUND'
            )
        except ValidationError as e:
            return ServiceResponse.error(
                message="Validation failed",
                errors=e.message_dict if hasattr(e, 'message_dict') else str(e),
                code='VALIDATION_ERROR'
            )
        except Exception as e:
            logger.error(f"Error updating {self.model.__name__}: {e}", exc_info=True)
            return ServiceResponse.error(
                message="Update failed",
                errors=str(e),
                code='UPDATE_ERROR'
            )
    
    def bulk_update(self, updates: List[Dict[str, Any]], 
                    update_fields: List[str]) -> Dict[str, Any]:
        """
        Update multiple records in bulk
        
        Args:
            updates: List of dicts with 'id' and fields to update
            update_fields: List of field names to update
            
        Returns:
            ServiceResponse with update count
        """
        try:
            with transaction.atomic():
                instances = []
                ids = [item['id'] for item in updates]
                existing = {obj.pk: obj for obj in self.model.objects.filter(pk__in=ids)}
                
                for update_data in updates:
                    pk = update_data.pop('id')
                    if pk in existing:
                        instance = existing[pk]
                        for field, value in update_data.items():
                            if field in update_fields:
                                setattr(instance, field, value)
                        instances.append(instance)
                
                self.model.objects.bulk_update(instances, update_fields)
                
                logger.info(f"Bulk updated {len(instances)} {self.model.__name__} records")
                
                return ServiceResponse.success(
                    data={'count': len(instances)},
                    message=f"{len(instances)} records updated successfully"
                )
                
        except Exception as e:
            logger.error(f"Error in bulk update: {e}", exc_info=True)
            return ServiceResponse.error(
                message="Bulk update failed",
                errors=str(e),
                code='BULK_UPDATE_ERROR'
            )
    
    # ==================== DELETE OPERATIONS ====================
    
    def delete(self, pk: int, soft_delete: bool = False) -> Dict[str, Any]:
        """
        Delete a record
        
        Args:
            pk: Primary key value
            soft_delete: Soft delete by setting is_active=False
            
        Returns:
            ServiceResponse
        """
        try:
            with transaction.atomic():
                instance = get_object_or_404(self.model, pk=pk)
                
                if soft_delete and hasattr(instance, 'is_active'):
                    instance.is_active = False
                    instance.save()
                    action = "deactivated"
                else:
                    instance.delete()
                    action = "deleted"
                
                logger.info(f"{action.capitalize()} {self.model.__name__} ID {pk}")
                
                return ServiceResponse.success(
                    message=f"{self.model.__name__} {action} successfully"
                )
                
        except ObjectDoesNotExist:
            return ServiceResponse.error(
                message=f"{self.model.__name__} not found",
                code='NOT_FOUND'
            )
        except Exception as e:
            logger.error(f"Error deleting {self.model.__name__}: {e}", exc_info=True)
            return ServiceResponse.error(
                message="Delete failed",
                errors=str(e),
                code='DELETE_ERROR'
            )
    
    def bulk_delete(self, ids: List[int], soft_delete: bool = False) -> Dict[str, Any]:
        """
        Delete multiple records
        
        Args:
            ids: List of primary keys
            soft_delete: Soft delete by setting is_active=False
            
        Returns:
            ServiceResponse with delete count
        """
        try:
            with transaction.atomic():
                queryset = self.model.objects.filter(pk__in=ids)
                count = queryset.count()
                
                if soft_delete and hasattr(self.model, 'is_active'):
                    queryset.update(is_active=False)
                    action = "deactivated"
                else:
                    queryset.delete()
                    action = "deleted"
                
                logger.info(f"Bulk {action} {count} {self.model.__name__} records")
                
                return ServiceResponse.success(
                    data={'count': count},
                    message=f"{count} records {action} successfully"
                )
                
        except Exception as e:
            logger.error(f"Error in bulk delete: {e}", exc_info=True)
            return ServiceResponse.error(
                message="Bulk delete failed",
                errors=str(e),
                code='BULK_DELETE_ERROR'
            )
    
    # ==================== UTILITY METHODS ====================
    
    def exists(self, **filters) -> bool:
        """Check if record exists with given filters"""
        return self.model.objects.filter(**filters).exists()
    
    def count(self, **filters) -> int:
        """Count records with given filters"""
        return self.model.objects.filter(**filters).count()
    
    def get_or_create(self, defaults: Optional[Dict] = None, 
                      **kwargs) -> Dict[str, Any]:
        """Get or create a record"""
        try:
            instance, created = self.model.objects.get_or_create(
                defaults=defaults, **kwargs
            )
            return ServiceResponse.success(
                data={
                    'object': self._serialize_instance(instance),
                    'created': created
                },
                message="Record retrieved" if not created else "Record created"
            )
        except Exception as e:
            return ServiceResponse.error(
                message="Get or create failed",
                errors=str(e)
            )
    
    def _prepare_data(self, data: Dict[str, Any], 
                      partial: bool = False) -> Dict[str, Any]:
        """Prepare and clean data before save"""
        # Remove None values in partial updates
        if partial:
            return {k: v for k, v in data.items() if v is not None}
        return data
    
    def _serialize_instance(self, instance: models.Model, 
                           include_relations: bool = False) -> Dict[str, Any]:
        """
        Serialize model instance to dictionary
        Override this method for custom serialization
        """
        data = {}
        
        for field in instance._meta.fields:
            value = getattr(instance, field.name)
            
            # Handle special field types
            if isinstance(field, models.DateTimeField) and value:
                data[field.name] = value.isoformat()
            elif isinstance(field, models.DateField) and value:
                data[field.name] = value.isoformat()
            elif isinstance(field, models.ImageField) and value:
                data[field.name] = value.url if value else None
            elif isinstance(field, models.FileField) and value:
                data[field.name] = value.url if value else None
            elif isinstance(field, models.ForeignKey) and value:
                if include_relations:
                    data[field.name] = {
                        'id': value.pk,
                        'name': str(value)
                    }
                else:
                    data[field.name] = value.pk
            else:
                data[field.name] = value
        
        return data
