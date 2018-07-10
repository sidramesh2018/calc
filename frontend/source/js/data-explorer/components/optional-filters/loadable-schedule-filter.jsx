import LoadableWrapper from '../loadable-wrapper';

const LoadableScheduleFilter = LoadableWrapper(
  () => import('./schedule-filter'));

export default LoadableScheduleFilter;
