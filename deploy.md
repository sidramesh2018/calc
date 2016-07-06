### Deploying to Cloud Foundry

###### Only of interest to 18F team members

If you don’t already have one, request a Cloud Foundry account in #devops
in Slack and download the Cloud Foundry CLI according to the instructions here:
https://docs.18f.gov/getting-started/setup/

To start, target the org and space you want to work with. For example, if you wanted to work with the staging space:
`cf target -o oasis -s calc-dev`

Manifest files, which contain import deploy configuration settings, are located
in the [manifests](manifests/) directory of this project.

#### CF Structure
- Organization: `oasis`
- Spaces: `calc-dev`, `calc-prod`
- Apps:
  - calc-dev space:
    - calc-dev
- Routes:
  - calc-dev.apps.cloud.gov -> calc-dev space, calc-dev app

TODO: Structure for production deployment once determined

#### Environment Variables

For cloud.gov deployments, this project makes use of a
[User Provided Service (UPS)][UPS] to get its configuration
variables, instead of using the local environment. You will need to create a
UPS called `calc-env`, provide 'credentials' to it, and link it to the
application instance. This will need to be done for every Cloud Foundry `space`.

First, create a file with a name like `credentials-staging.json` with all the configuration values specified as per the "Environment Variables" section of
[`README.md`][]:

```json
{
  "SECRET_KEY": "my secret key",
  "...": "other environment variables"
}
```

Then enter the following commands (assuming you already have an application
instance named `calc-dev`):

```sh
cf cups calc-env -p credentials-staging.json
cf bind-service calc-dev calc-env
cf restage calc-dev
```

You can update the user provided service with the following commands:

```sh
cf uups calc-env -p credentials-staging.json
cf restage calc-dev
```

#### Staging Server

The staging server updates automatically when changes are merged into the
`develop` branch. Check out the `deploy` section of [.travis.yml](.travis.yml)
for details and settings.

Should you need to, you can push directly to calc-dev.apps.cloud.gov with:

`cf push -f manifests/manifest-staging.yml`

Remember to target the `calc-dev` space first (`cf target -s calc-dev`).

#### Your Own Server

If you want to deploy to your own sandbox, e.g. for the purpose of deploying a branch you're working on, see the wiki page on [How to Deploy to your Sandbox](https://github.com/18F/calc/wiki/How-to-Deploy-to-your-Sandbox).

There is an example sandbox manifest at [manifests/manifest-sandbox.yml](manifests/manifest-sandbox.yml)

#### Production Servers

TODO Production application development once determined

### Setting up the API

In production, CALC's public API is actually fronted by an [API Umbrella][]
instance on api.data.gov which proxies all API requests to CALC. This
allows CALC to not have to concern itself with details like API keys and
rate limiting.

In order to configure the proxying between api.data.gov and CALC,
you will need to obtain an administrative account on api.data.gov.
For more information on doing this, see the [api.data.gov User Manual][].

You'll then want to tell api.data.gov what host it will listen for, and
what host your API backend is listening on. For example:

| Frontend Host   | Backend Host   |
| --------------- | -------------- |
| api.data.gov    | calc.gsa.gov   |

You will also want to configure your API backend on
api.data.gov with one **Matching URL Prefixes** entry.
The **Backend Prefix** should always be `/api/`, while the
**Frontend Prefix** is up to you. Here's an example:

| Frontend Prefix | Backend Prefix |
| --------------- | -------------- |
| /gsa/calc/      | /api/          |

Now you'll need to configure `API_HOST` on your CALC instance to be
the combination of your **Frontend Host** and **Frontend Prefix**.
For example, given the earlier examples listed above, your
`API_HOST` setting on CALC would be `https://api.data.gov/gsa/calc/`.

Finally, as mentioned in the [Securing your API backend][] section of the
user manual, you will likely need to configure `WHITELISTED_IPS` on
your CALC instance to ensure that clients can't bypass rate limiting by
directly contacting your CALC instance.

[UPS]: https://docs.cloudfoundry.org/devguide/services/user-provided.html
[`README.md`]: https://github.com/18F/calc#readme
[API Umbrella]: https://apiumbrella.io/
[api.data.gov User Manual]: https://github.com/18F/api.data.gov/wiki/User-Manual:-Agencies
[Securing your API backend]: https://github.com/18F/api.data.gov/wiki/User-Manual:-Agencies#securing-your-api-backend
