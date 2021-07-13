#! /usr/bin/python3

import yaml, re, sys


def main():
    if len(sys.argv) != 3:
        report_and_exit("Usage: deployment-mapper ref-to-deploy deployment-spec-file.yaml")
    ref = sys.argv[1]
    deployment_spec = sys.argv[2]
    try:
        with open(deployment_spec) as file:
            spec = yaml.load(file, Loader=yaml.FullLoader)
            name = spec.get('name') or report_and_exit("Problem with deployment spec: couldn't find image.name")
            version = spec.get("version")
            if version:
                if (version == 2): 
                    print(f'image={name}')
                    print(f'::set-output name=image::{name}')
                    find_ref(spec, ref)
                else:
                    report_and_exit( f'Unknown file version: {version}' )
            else:
                version1(name, spec, ref) 
    except FileNotFoundError:
        report_and_exit( f'Could not find deployment specification file {deployment_spec}' )


def version1(name, spec, ref):
    validate1(spec)
    env = find_deployment1(spec, ref)
    if env:
        print(f'image={name}/{env}')
        print(f'::set-output name=image::{name}/{env}')


def validate1(spec):
    deployments = spec.get('deployments')
    if not deployments:
        report_and_exit("Problem with deployment spec: couldn't find deployments")
    if not isinstance(deployments, list):
        report_and_exit("Problem with deployment spec: deployments should be an ordered list of environments")
    if not all( legal_env_spec1(es) for es in deployments):
        report_and_exit("Problem with deployment spec: each environment spec should have a tag or branch specified")


def find_deployment1(spec, ref):
    target = re.sub('refs/(tags|heads)/','', ref)
    for deployment in spec.get('deployments'):
        for k, p in deployment.items():
            pattern = p.get('tag') if ref.startswith("refs/tags/") else p.get('branch')
            if (pattern):
                pattern = pattern.replace("{ver}", "[0-9][0-9\\.]*")
                if re.fullmatch(pattern, target):
                    print(f'target={target}')
                    print(f'::set-output name=target::{target}')
                    return k
    return None


def legal_env_spec1(es):
    if isinstance(es, dict):
        for env, spec in es.items():
            if spec.get('tag') or spec.get('branch'):
                return True
            else:
                report_and_exit(f'Problem with deployment spec: {env} does not specific tag or branch pattern')
    return False


def parse_dict(init, lkey=''):
    ret = {}
    for rkey,val in init.items():
        key = lkey+rkey
        if isinstance(val, dict):
            ret.update(parse_dict(val, key+'.'))
        else:
            ret[key] = val
    return ret


def find_ref(spec, ref):
    target = re.sub('refs/(tags|heads)/','', ref)
    for d in spec.get('deployments'):
        if d.get('tag'):
            pattern = d.pop('tag')
        elif d.get('branch'):
            pattern = d.pop('branch')
        if (pattern):
            pattern = pattern.replace("{ver}", "[0-9][0-9\\.]*")
            try: 
                if re.fullmatch(pattern, target):
                    print(f'target={target}')
                    print(f'::set-output name=target::{target}')
                    for k,v in parse_dict(d, '').items():
                        print(f'{k}={v}')
                        print(f'::set-output name={k}::{v}')
            except:
                report_and_exit( f'Invalid regexp "{pattern}"' )


def report_and_exit(message):
    print(message, file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
