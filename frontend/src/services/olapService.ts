import { api } from './api';
import { OLAPDimension, OLAPMeasure, OLAPResult } from '@/types';

export interface DimensionSelect {
  dimension: string;
  attribute: string;
}

export interface FilterClause {
  dimension: string;
  attribute: string;
  operator?: string;
  value?: any;
  values?: any[];
}

export const olapService = {
  getDimensions: (): Promise<OLAPDimension[]> =>
    api.get('/olap/dimensions').then((r) => r.data),
  getMeasures: (): Promise<OLAPMeasure[]> => api.get('/olap/measures').then((r) => r.data),
  getCubeMetadata: () => api.get('/olap/cube/metadata').then((r) => r.data),

  query: (payload: {
    dimensions: DimensionSelect[];
    measures: string[];
    filters?: FilterClause[];
    grouping_mode?: string;
    order_by?: string[];
    limit?: number;
  }): Promise<OLAPResult> => api.post('/olap/query', payload).then((r) => r.data),

  slice: (payload: any) => api.post('/olap/slice', payload).then((r) => r.data),
  dice: (payload: any) => api.post('/olap/dice', payload).then((r) => r.data),
  drillDown: (payload: any) => api.post('/olap/drill-down', payload).then((r) => r.data),
  rollUp: (payload: any) => api.post('/olap/roll-up', payload).then((r) => r.data),
  pivot: (payload: any) => api.post('/olap/pivot', payload).then((r) => r.data),
  cubeAggregate: (payload: any) => api.post('/olap/cube/aggregate', payload).then((r) => r.data),
};
