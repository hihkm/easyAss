def split_test(prefix, code_str, _with_bracket):
    code_str = code_str[len(prefix):].strip('() ')
    args = code_str.split()
    print(code_str)



split_test(r'\move', r'\move  (  1923,150,-26,150) ')
