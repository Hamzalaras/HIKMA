import { readdir } from 'fs/promises';
import { pathToFileURL } from 'url';
import { join } from 'path';

export const eventHandler = async (myBot) => {
    const eventFolderPath = join(import.meta.dirname, '..', 'events');

    const eventFiles = (await readdir(eventFolderPath, { withFileTypes: true }))
        .filter(file => file.isFile() && file.name.endsWith('.js'));

    for (const file of eventFiles) {
        const filePath = join(eventFolderPath, file.name);

        const fileUrl = pathToFileURL(filePath).href;
        const { default: event } = await import(fileUrl);

        if (event && event.name && typeof event.execute === 'function') {
            const method = event.once ? 'once' : 'on'
            myBot[method](event.name, (...args) => event.execute(...args));
        }
    }
};