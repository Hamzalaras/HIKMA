import { KATHER_STATUS } from '../constants/https.js';
import { ApiFetchError, NotFoundError } from './errors/Errors.js';
import { fetchFunc } from './fetchFunc.js';

export const fetchAndValidate = async ({ url, signal, errorMessage, expectArray = false }) => {
    const data = await fetchFunc({ url, signal });
    
    if (!data) {
        throw new ApiFetchError(`${errorMessage}: fetchFunc returned null`);
    }
    
    const hasData = expectArray ? data.data?.length : data.data;
    if (data.status !== KATHER_STATUS.SUCCESS || !hasData) {
        throw new NotFoundError(`No data found: ${errorMessage}`);
    }
    
    return data;
};

export const formatAutocompleteData = (items, query = '') => {
    if (!Array.isArray(items)) return [];
    
    const lowerQuery = query.toLowerCase();

    return items
        .filter(item => {
            if (!lowerQuery) return true;
            
            const searchFields = [
                item.name, 
                item.name_ar, 
                item.name_en, 
                ...(item.aliases || [])
            ].filter(Boolean).map(name => name.toLowerCase());

            return searchFields.some(name => name.includes(lowerQuery));
        })
        .map(item => ({
            name: item.name || item.name_ar || item.name_en,
            value: `${item.id}`
        }));
};

export const resolveId = async (val, route) => {
    const resolvedVal = Number.parseInt(val, 10);

    if (!isNaN(resolvedVal)) return resolvedVal;

    const res = await fetchAndValidate({
        url: `${route}?q=${encodeURIComponent(val)}`,
        errorMessage: `Failed to resolve: ${val}`,
        expectArray: true
    });

    return res.data[0]?.id;
};