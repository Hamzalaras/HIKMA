import { readdir } from 'fs/promises';
import { pathToFileURL } from 'url';
import { join } from 'path';

export const commandHandler = async (myBot) => {
    const commandsFolderPath = join(import.meta.dirname, '..', 'commands');
    const folders = (await readdir(commandsFolderPath, { withFileTypes: true }))
                        .filter(folder => folder.isDirectory());

    for (const folder of folders) {
        const folderPath = join(commandsFolderPath, folder.name);
        const files = (await readdir(folderPath,{ withFileTypes: true }))
                        .filter(file => file.isFile() && file.name.endsWith('.js'));

        for (const file of files) {
            const filePath = join(folderPath, file.name);

            const fileUrl = pathToFileURL(filePath).href;
            const { default: command } = await import(fileUrl);

            if  (command && command.execute) {
                const commandName = command.data?.name || command.name;
                myBot.commands.set(commandName, command);
            }
        }
    }
};