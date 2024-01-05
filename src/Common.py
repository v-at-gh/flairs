#TODO: remove `shell=True` argument and implement command splitter
subprocess_run_args_str = "shell=True, capture_output=True, text=True, encoding='utf8'"

subprocess_run_kwargs = {}
for arg in subprocess_run_args_str.split(', '):
    key, value = arg.split('=')
    subprocess_run_kwargs[key] = eval(value)

del subprocess_run_args_str
