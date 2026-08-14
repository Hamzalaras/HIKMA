import { KATHER_ROUTES, KATHER_ENDPOINTS } from '../constants/https.js';
import { COMMAND_OPTIONS } from '../constants/options.js';
import { buildQuery } from '../utils/builders/meta.builders.js';
import { fetchAndValidate, formatAutocompleteData, resolveId } from '../utils/service.helpers.js';

const POET_AUTOCOMPLETE_URLS = {
    [COMMAND_OPTIONS.POET.ERA]: () => `${KATHER_ROUTES.CATALOG}${KATHER_ENDPOINTS.CATALOG.ERA}`,
    [COMMAND_OPTIONS.POET.COUNTRY]: () => `${KATHER_ROUTES.CATALOG}${KATHER_ENDPOINTS.CATALOG.COUNTRY}`,
};

export const getPoet = async ({ poetId, gender, era, country }) => {

    let url = `${KATHER_ROUTES.POETS}`;

    if (poetId) {
        const resolvedPoetId = await resolveId(poetId, KATHER_ROUTES.POETS);
        url += `/${resolvedPoetId}`;
    } else {
        url += `/random${buildQuery({ gender, era, country })}`;
    }

    const res = await fetchAndValidate({ url, errorMessage: 'Error fetching poet data' });
    return res.data;
};

export const getPoetAutocomplete = async ({ optionName, optionValue, signal }) => {
    const getUrl = POET_AUTOCOMPLETE_URLS[optionName] 
        || ((val) => `${KATHER_ROUTES.POETS}?q=${encodeURIComponent(val)}&limit=25`);

    try {
        const res = await fetchAndValidate({ url: getUrl(optionValue), signal, errorMessage: 'Poet autocomplete failed' });
        return formatAutocompleteData(res.data, optionValue);
    } catch {
        return [];
    }
};