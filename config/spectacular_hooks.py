"""drf_spectacular hooks for modifying OpenAPI schema.
    Omo we could implement a less code-stressing OpenAPI schema,
    using other library other than drf_spectacular. 
    Like drf_yasg:-> https://pypi.org/project/drf-yasg/
    This will give us the chance to organize stuff
"""


def modify_community_tags(result, generator, request, public, **kwargs):
    """
    Postprocessing hook that tags /api/v1/posts/* endpoints with Community tag.
    """
    paths = result.get('paths', {})
    
    for path, path_item in paths.items():
        if '/api/v1/posts' in path:
            # For all post-related endpoints, set the Community tag
            for method, operation in path_item.items():
                if isinstance(operation, dict) and 'tags' in operation:
                    # Only replace 'v1' tag with 'Community', keep 'Community' as is
                    if 'v1' in operation['tags']:
                        operation['tags'] = ['Community']
    
    return result
