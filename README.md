# crdm-tools

## Access to private GitHub repos from GAE

To be able to clone GitHub repos on a GAE, create a new
[fine-grained personal access token](https://github.com/settings/personal-access-tokens),
make sure the "Resource owner" is set to `uclh-criu` and then select the repositories you want to access.
Submit the request to generate the token and then make sure to copy the token to a safe place as it will not be shown again!

First store your PAT in a file on the GAE in the path `~/.pat.txt`, then
configure `git` to use the token by running the following command:

```shell
git config --global credential.helper 'store --file ~/.pat.txt'
```

This process needs to be repeated for every GAE.

Additionally record the token in the `GITHUB_PAT` environment variable in the `.env` file in this
repository's root.
