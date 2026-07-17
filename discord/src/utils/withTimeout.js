

export const withTimeout = async ({ fn, passedSignals = [], timeout = 5_000 }) => {
    const controller = new AbortController ();
    const signal = controller.signal;
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    const resolvedSignal = passedSignals.length > 0 ? 
                                AbortSignal.any([ signal, ...passedSignals ]) :
                                signal;
    try {
        const response = await fn({ signal: resolvedSignal });
        return response;
    } catch (error) {
        throw error;
    } finally {
        clearTimeout(timeoutId);
    }
};