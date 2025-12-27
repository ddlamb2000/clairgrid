import resource

def report_memory_resource():
    print(f"ℹ Memory resource: {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1000} MB")