
export const fetchFunc = async ({ url, signal }) => {

    const response = await fetch(url, { signal });

    const contentType = response?.headers?.get('content-type');
    if (!contentType || !contentType.includes('application/json')) return null;
    const data = await response.json();
    return data;
};