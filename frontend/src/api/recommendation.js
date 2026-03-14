import request from '@/utils/request';

const API_URL = '/recommendation/';

export const getRecommendations = (params) => {
    return request({
        url: `${API_URL}recommendations/`,
        method: 'get',
        params
    });
};
