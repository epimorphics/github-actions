# A collection of Github Actions

## ansible

Install Ansible on github runner host. 
Also configures AWS credentials and ssh configuration from github to AWS.

### Inputs

| Name | Description | Default |
|---|---|---|
| `aws-access-key-id` | the git ref which triggered the action | |
| `aws-secret-access-key` | name of the file specifying the deployment pattern to use | `deployment.yaml` |
| `aws-profile` | AWS PRofile used by the github runner. | `aws` |
| `aws-region` | AWS Region | `eu-west-1` |
| `host-prefix` | Host name prefix used by ssh | |
| `key-file` | ssh identity file used by Ansible to connect to AWS ec2 hosts | `id_rsa` |
| `ssh-key` | ssh key used by Ansible to connect to AWS ec2 hosts | | 

### Outputs

None

## ansible-deploy-full

Run a full deploy via ansible.

### Inputs

| Name | Description | Default |
|---|---|---|
| `aws-profile` | AWS Profile | `aws` |
| `path` | Path to the `ansible` directory | `ansible` |
| `playbook` | Ansible playbook to run | `deply.yml` |
| `secret` | Secret for the Ansible Vault | | 
| `vault-secret-file` | Ansible Vault Secret file | `.secret/default` |

### Outputs

None

## ansible-deploy-image

Run a tag deploy via ansible.

### Inputs

| Name | Description | Default |
|---|---|---|
| `aws-profile` | AWS Profile | `aws` |
| `path` | Path to the `ansible` directory | `ansible` |
| `playbook` | Ansible playbook to run | `deply.yml` |
| `name` | ansible-tag/image to deploy | | 
| `stage` | The Environment/Stage to update | | 
| `secret` | Secret for the Ansible Vault | | 
| `vault-secret-file` | Ansible Vault Secret file | `.secret/default` |
| `version` | Version (docker tag) of the image to deploy | |

### Outputs

None

## ansible-vault-secret

Install a Ansible Vault Secret.

### Inputs

| Name | Description | Default |
|---|---|---|
| `path` | Path to the `ansible` directory | `ansible` |
| `secret` | Secret for the Ansible Vault | | 
| `vault-secret-file` | Ansible Vault Secret file | `.secret/default` |

### Outputs

None.

## create-ecr-action

Creates (if needs) an AWS ECR.

### Inputs

| Name | Description | Default |
|---|---|---|
| `image` | Name of the ECR repository | |
| `region` | AWS Region | `eu-west-1` |

### Outputs

None

## git-info-action

Returns extra git hub information.

### Inputs

| Name | Description | Default |
|---|---|---|
| `path` | Directory of the repository | `.` |

### Outputs

| Name | Description | Default |
|---|---|---|
| `tag` | Latest tag | `.` |

# mapper

GH Action for declaratively mapping deployments

This action supports a continuous deployment approach in which the mapping from a pushed commit or tag to a deployment environment is specified in a declarative mapping file, expressed in yaml.

It is designed for use with AWS ECR docker image repositories and for a pattern where there is a separate image repository for each target environment. The job of this action is determine if the pushed commit or tag should trigger an image build and if so which image name and repository to build and push to.

## Inputs

| Name | Description | Default |
|---|---|---|
| `ref` | the git ref which triggered the action | |
| `mapFile` | name of the file specifying the deployment pattern to use | `deployment.yaml` |

## Outputs

| Name | Description |
|---|---|
| `image` | name of environment-specific image to build |
| `target` | The target Stage/Environment | |

If the push should not trigger a build then the action will still succeed but `image` will not be bound.

## Example usage

```yaml
name: Mapped deployment
on:
  push: {}

jobs:
  mapped-deploy:
    name: mapped-deployment
    runs-on: ubuntu-18.04
    steps:
    - uses: actions/checkout@v2
    - name: "Check for mapped deployment"
      id: mapper
      uses: epimorphics/github-actions/mapper@v2
      with:
        ref: "${{github.ref}}"
```

## Deployment specification file

### Version 1

A deployment pattern is specified in a yaml file with a structure like:

```yaml
name:  epimorphics/myapp
deployments:
  - production:
      tag: "{ver}"
  - staging:
      tag: "{ver}-rc.*"
      branch: staging
  - dev:
      branch: "master|main"
```

The `deployments` section is a list of environment patterns. Each of which has the environment name as a key and a `tag` or `branch` regular expression (or both). If the pushed git reference is a tag it will be matched against the tag patterns, otherwise it will be matched against the branch patterns. The patterns can include `{ver}` which is mapped to a loose regular expression for sequences of digits and `.` characters as used in semver tagging.

The first environment which matches the ref is chosen, if no environment patterns match then no outputs are bound.

The generated `image` name follows the pattern

    {name}/{env}

For example: `epimorphics/myapp/production`

The `aws` information is extracted from the specification by this action just to avoid later workflow steps having to do a repeat parse. The `aws.region` is optional and defaults to `eu-west-1`.

### Version 2

In version 2 of the `deployment.yaml` file the deployement struction is turned inside-out. 
If the version is not specified version 1 (above) is assumed.

If the name field is present in the deployments.yaml this is returned as `image`.
This is differenet behaviour to Version 1 (see above).

Each deployment is considered in turn. If tag or branch matches the current context `target` is returned. Where `target` is the matched version or branch.
If the deployment contains either `deploy` or `publish` these are also returned. 

```yaml
version: 2
name:  epimorphics/nrw-bwq-widgets
deployments:
  - tag: "v{ver}"
    deploy: prod
    publish: prod
  - branch: "test"
  - tag: "v{ver}-rc"
    deploy: preprod
    publish: prod
    deploy: test
    publish: test
  - branch: "[a-zA-Z0-9]+"
```
It is assumed that 
- if a match is made for a deployment and a value for `target` returned then an image will be created (and potentially tested).

- if `publish` is present for a deployment then the image will be published.

- if `env` is present for a deployment then the image will be deployed.
