import { KATHER_ROUTES, KATHER_ENDPOINTS } from '../constants/https.js';
import { COMMAND_OPTIONS } from '../constants/options.js';
import { buildQuery } from '../utils/builders/meta.builders.js';
import { fetchAndValidate, formatAutocompleteData, resolveId } from '../utils/service.helpers.js';

const LINES_AUTOCOMPLETE_URLS = {
    [COMMAND_OPTIONS.LINE.POEM]: (val) => `${KATHER_ROUTES.POEMS}?q=${encodeURIComponent(val)}`,
    [COMMAND_OPTIONS.LINE.POET]: (val) => `${KATHER_ROUTES.POETS}?q=${encodeURIComponent(val)}&limit=25`,
    [COMMAND_OPTIONS.LINE.ERA]: () => `${KATHER_ROUTES.CATALOG}${KATHER_ENDPOINTS.CATALOG.ERA}`,
    [COMMAND_OPTIONS.LINE.COUNTRY]: () => `${KATHER_ROUTES.CATALOG}${KATHER_ENDPOINTS.CATALOG.COUNTRY}`,
    [COMMAND_OPTIONS.LINE.TOPIC]: () => `${KATHER_ROUTES.CATALOG}${KATHER_ENDPOINTS.CATALOG.TOPIC}`,
    [COMMAND_OPTIONS.LINE.QUAFIA]: () => `${KATHER_ROUTES.CATALOG}${KATHER_ENDPOINTS.CATALOG.QUAFIA}`,
    [COMMAND_OPTIONS.LINE.SEA]: () => `${KATHER_ROUTES.CATALOG}${KATHER_ENDPOINTS.CATALOG.SEA}`,
};

export const getSingleLine = async ({ lineId, poemId, poetId, lineType, gender, era, country, poemType, topic, quafia, sea }) => {
    let url = `${KATHER_ROUTES.LINES}`;

    if (lineId) {
        const resolvedLineId = await resolveId(lineId, KATHER_ROUTES.LINES);
        url += `/${resolvedLineId}`
    } else if (poemId) {
        const resolvedPoemId = await resolveId(poemId, KATHER_ROUTES.POEMS);
        url += `/random${buildQuery({ poemId: resolvedPoemId })}`;
    } else if (poetId) {
        const resolvedPoetId = await resolveId(poetId, KATHER_ROUTES.POETS);
        url += `/random${buildQuery({ poetId: resolvedPoetId })}`;
    } else {
        url = `${KATHER_ROUTES.LINES}/random${buildQuery({ 
            lineType, gender, era, country, poemType, topic, quafia, sea 
        })}`;
    }

    const res = await fetchAndValidate({ url, errorMessage: 'Error fetching single line data' });
    return res.data;
};

export const getLines = async ({ poetId, poemId, lineType, gender, era, country, poemType, topic, quafia, sea, page = 1, limit = 50 }) => {
    const offset = (page - 1) * limit;
    let queryParams;

    if (poemId) {
        const resolvedPoemId = await resolveId(poemId, KATHER_ROUTES.POEMS);
        queryParams = { poemId: resolvedPoemId, limit, offset };
    } else if (poetId) {
        const resolvedPoetId = await resolveId(poetId, KATHER_ROUTES.POETS);
        queryParams = { poetId: resolvedPoetId, limit, offset };
    } else {
        queryParams = { 
            gender, era, country, poemType, topic, quafia, sea,
            lineType, limit, offset 
        };
    }

    const url = `${KATHER_ROUTES.LINES}${buildQuery(queryParams)}`;
    const res = await fetchAndValidate({ url, errorMessage: 'Error fetching lines data', expectArray: true });
    return res;
};

export const getLinesAutocomplete = async ({ optionName, optionValue, signal }) => {
    const getUrl = LINES_AUTOCOMPLETE_URLS[optionName];
    if (!getUrl) return [];

    try {
        const res = await fetchAndValidate({ url: getUrl(optionValue), signal, errorMessage: 'Lines autocomplete fetch failed' });
        return formatAutocompleteData(res.data, optionValue);
    } catch {
        return [];
    }
};

export const getSingleLineAutocomplete = async ({ optionName, optionValue, signal }) => {
    if (optionName === COMMAND_OPTIONS.LINE.LINE_ID) {
        const url = `${KATHER_ROUTES.LINES}?q=${encodeURIComponent(optionValue)}&limit=25`;
        try {
            const res = await fetchAndValidate({ url, signal, errorMessage: 'Single line autocomplete failed' });
            if (!res.data) return [];
            
            return res.data.map(ele => ({
                name: ele.content.length > 95 ? `${ele.content.substring(0, 92)}...` : ele.content,
                value: `${ele.id}`
            }));
        } catch {
            return [];
        }
    }

    return getLinesAutocomplete({ optionName, optionValue, signal });
};