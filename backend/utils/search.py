import jieba
from django.db.models import Q
from rest_framework import filters

def get_jieba_keywords(text):
    """
    Segment text using jieba (search mode) and return a list of keywords.
    Filters out single characters and empty strings.
    """
    if not text:
        return []
    
    # Segment using search mode for better recall
    words = list(jieba.cut_for_search(text))
    # Filter: length > 1 and not just whitespace
    keywords = [w.strip() for w in words if len(w.strip()) > 1]
    
    if not keywords:
        # If no multi-char keywords found, fall back to the original text
        keywords = [text.strip()]
        
    return keywords

class JiebaSearchFilter(filters.SearchFilter):
    """
    Custom DRF SearchFilter that segments the search query using jieba.
    """
    def filter_queryset(self, request, queryset, view):
        search_terms = self.get_search_terms(request)
        search_fields = getattr(view, 'search_fields', None)

        if not search_fields or not search_terms:
            return queryset

        # Combine all search terms into one string for segmentation
        full_query = " ".join(search_terms)
        keywords = get_jieba_keywords(full_query)

        base_queries = []
        for keyword in keywords:
            field_queries = []
            for field in search_fields:
                # Default to icontains for all fields
                lookup = f"{field}__icontains"
                field_queries.append(Q(**{lookup: keyword}))
            
            # OR all fields for a single keyword
            if field_queries:
                combined_field_query = field_queries[0]
                for q in field_queries[1:]:
                    combined_field_query |= q
                base_queries.append(combined_field_query)

        # AND all keywords together (every keyword must match at least one field)
        # This is generally what users expect: searching "Java 后端" means "Java" AND "后端"
        if base_queries:
            final_query = base_queries[0]
            for q in base_queries[1:]:
                final_query &= q
            return queryset.filter(final_query).distinct()

        return queryset
