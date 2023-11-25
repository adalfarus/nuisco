import build
import template

def console_script(command_line):
    # Format : nuisca subcmd --args --arglst
    # Example : nuisca build --arg=arg --arglst=123, 1222 --arglst=123 1222 --arglst=123,1222 --arglst=123, 1222 123 1222, 123,1222
    # Output --> nuisca.build(arg=arg, arglst=123, 1222, 123, 1222, 123, 1222, 123, 1222, 123, 1222, 123, 1222)
    parts = command_line.split()
    
    if len(parts) < 2:
        raise ValueError("Invalid command format")
    
    subcmd = parts[1]
    kwargs = {}
    key = None

    for part in parts[2:]:
        if part.startswith('--'):
            key = part[2:]
            kwargs[key] = []
        elif key is not None:
            values = part.replace(',', ' ').split()
            kwargs[key].extend(values)
        else:
            raise ValueError("Invalid argument format")

    # Convert lists with a single item to that item
    for arg in kwargs:
        if isinstance(kwargs[arg], list) and len(kwargs[arg]) == 1:
            kwargs[arg] = kwargs[arg][0]

    # Handling different sub-commands
    if subcmd == 'build':
        func = getattr(build, 'build_main', None)
        if not func:
            raise ValueError(f"build_main function not found in build module")
    elif subcmd == 'create-template':
        if len(parts) < 3:
            raise ValueError("Project name is required for create-template")
        project_name = parts[2]
        func = getattr(build, 'create_template', None)
        if not func:
            raise ValueError(f"create_template function not found in build module")
        return func(project_name, **kwargs)
    else:
        raise ValueError(f"Unknown subcommand: {subcmd}")

    # Call the function with unpacked arguments
    return func(**kwargs)

# Example usage
command_line = "nuisca build --arg=arg --arglst=123, 1222"
console_script(command_line)
