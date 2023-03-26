# download github repos used in PA experiments

import os,sys

def main():
    def download(repo):
        print('downloading ',repo)
        os.system(f'git clone --depth=1 --branch {repo_tag[repo]} {repo_url[repo]}')
        #os.system(f'git clone {repo_map[repo]}')
        #os.system(f'cd {repo} && git checkout {repo_branch[repo]}')
    
    urls = ['https://github.com/numpy/numpy',
    'https://github.com/scipy/scipy',
    'https://github.com/matplotlib/matplotlib',
    'https://github.com/pandas-dev/pandas',
    'https://github.com/sympy/sympy',
    'https://github.com/django/django',
    'https://github.com/scikit-learn/scikit-learn',
    'https://github.com/pytorch/pytorch',
    'https://github.com/blender/blender']

    # use the highest-numbered non-"rc" tag as of 22dec2021.
    repo_tag = { 'blender' : 'v3.0.0'
     ,'django' : '4.0'
     ,'matplotlib': 'v3.5.1'
     ,'numpy' : 'v1.21.5'
     ,'pandas' : 'v1.3.5'
     ,'pytorch' : 'v1.10.1'
     ,'scikit-learn' : '1.0.1'
     ,'scipy' : 'v1.7.3'
     ,'sympy' : 'sympy-1.9'
    }

    repo_url = {}
    for url in urls:
        repo_url[url.split('/')[-1]] = url

    if len(sys.argv) > 1:
        download(sys.argv[1])
    else:
        for repo in repo_url:
            download(repo)

main()
