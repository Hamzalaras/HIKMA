import { KATHER_ROUTES, KATHER_ENDPOINTS } from '../constants/https.js';
import { COMMAND_OPTIONS } from '../constants/options.js';
import { buildQuery } from '../utils/builders/meta.builders.js';
import { fetchAndValidate, formatAutocompleteData, resolveId } from '../utils/service.helpers.js';

const POEM_AUTOCOMPLETE_URLS = {
    [COMMAND_OPTIONS.POEM.ERA]: () => `${KATHER_ROUTES.CATALOG}${KATHER_ENDPOINTS.CATALOG.ERA}`,
    [COMMAND_OPTIONS.POEM.COUNTRY]: () => `${KATHER_ROUTES.CATALOG}${KATHER_ENDPOINTS.CATALOG.COUNTRY}`,
    [COMMAND_OPTIONS.POEM.TOPIC]: () => `${KATHER_ROUTES.CATALOG}${KATHER_ENDPOINTS.CATALOG.TOPIC}`,
    [COMMAND_OPTIONS.POEM.QUAFIA]: () => `${KATHER_ROUTES.CATALOG}${KATHER_ENDPOINTS.CATALOG.QUAFIA}`,
    [COMMAND_OPTIONS.POEM.SEA]: () => `${KATHER_ROUTES.CATALOG}${KATHER_ENDPOINTS.CATALOG.SEA}`,
};

export const getPoem = async ({ poemId, gender, era, country, poemType, topic, quafia, sea }) => {

    let url = `${KATHER_ROUTES.POEMS}`;

    if (poemId) {
        const resolvedPoemId = await resolveId(poemId, KATHER_ROUTES.POEMS);
        url += `/${resolvedPoemId}`;
    } else {
        url += `/random${buildQuery({ gender, era, country, poemType, topic, quafia, sea })}`;
    }

    const res = await fetchAndValidate({ url, errorMessage: 'Error fetching poem data' });
    return res.data;
};

export const getPoemAutocomplete = async ({ optionName, optionValue, signal }) => {
    const getUrl = POEM_AUTOCOMPLETE_URLS[optionName] 
        || ((val) => `${KATHER_ROUTES.POEMS}?q=${encodeURIComponent(val)}`);

    try {
        const res = await fetchAndValidate({ url: getUrl(optionValue), signal, errorMessage: 'Poem autocomplete failed' });
        return formatAutocompleteData(res.data, optionValue);
    } catch {
        return [];
    }
};