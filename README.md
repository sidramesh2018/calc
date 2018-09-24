# CALC

[![CircleCI](https://circleci.com/gh/18F/calc.svg?style=svg)](https://circleci.com/gh/18F/calc)
[![Code Climate](https://codeclimate.com/github/18F/calc/badges/gpa.svg)](https://codeclimate.com/github/18F/calc)
[![Test Coverage](https://codeclimate.com/github/18F/calc/badges/coverage.svg)](https://codeclimate.com/github/18F/calc/coverage)
[![Dependency Status](https://gemnasium.com/badges/github.com/18F/calc.svg)](https://gemnasium.com/github.com/18F/calc)

CALC is a tool to help contracting personnel estimate their per-hour labor costs for a contract, based on historical pricing information. The tool is live at [https://calc.gsa.gov](https://calc.gsa.gov). You can track progress or file an issue on this repo. See our [contributor guidelines](CONTRIBUTING.md).

## Documentation

To get started working on CALC, you'll probably want to start with
the [Docker setup guide](docs/docker.md).

The [CALC wiki](https://github.com/18F/calc/wiki) provides some context around
project history, how to orient yourself with the codebase, and how to do security reviews.

You may also find the following documents useful:

* [Change log](CHANGELOG.md)
* [Contributor guidelines](CONTRIBUTING.md)
* [License](LICENSE.md)


### Development documentation

The most readable version of the project's developer documentation
can be found at
[calc-dev.app.cloud.gov/docs/](https://calc-dev.app.cloud.gov/docs/).

The developer documentation is
also available in this repository's [docs](docs/) directory.


### API documentation

To get started with the CALC APIs, you can jump straight to the 
[CALC API documentation](https://calc-dev.app.cloud.gov/api/docs/)


### Front-end development and design documentation

We have a combined [style guide/component library](https://calc-dev.app.cloud.gov/styleguide/)
where we've documented things like site colors, form styles, page layout templates,
and our progressively enhanced widgets.


### System owner documentation

You may find it helpful to review our [guidelines on how to conduct
and document the weekly log and security event reviews.](https://github.com/18F/calc/wiki/Weekly-Log-and-Security-Event-Reviews)


### Team and task management documentation

The 18F CALC team managed sprints via [Zenhub](https://www.zenhub.com/) boards and epics.
Installing and using this extension might help clarify the relationship of some issues
to one another.

## Related work and CALC experiments

* [18F/calc-analysis](https://github.com/18F/calc-analysis) is a separate
  repository that contains data science experiments and other analyses that use CALC
  data.
* [Price prediction](https://github.com/18F/calc/pull/1562) was a feature explored
  with the intent of helping contracting officers make the best long-term decisions.
  Ultimately this was closed because of the difficulty of testing the accuracy of such a feature.
* [The CALC data dashboard](https://github.com/18F/calc/pull/1993) was a feature that gave
  users the ability to see a variety of stats about data in CALC, such as how recent it is.
  This was closed simply because the team had higher priorities, but could be easily explored in the future.
* [Changing the default data explorer dashboard](https://github.com/18F/calc/pull/1768) to show
  only the search box on load was a response to user confusion about what the graph and table
  show on page load. This idea could be explored further, but was closed because of lack
  of user testing.
