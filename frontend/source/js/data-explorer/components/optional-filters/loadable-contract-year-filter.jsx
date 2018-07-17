import LoadableWrapper from '../loadable-wrapper';

const LoadableContractYearFilter = LoadableWrapper(
  () => import('./contract-year-filter')
);

export default LoadableContractYearFilter;
