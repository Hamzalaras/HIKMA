import { REST, Routes } from 'discord.js';
import { readdir } from 'fs/promises';
import { pathToFileURL } from 'url';
import { join } from 'path';

const execute = async ({ message, args }) => {
        const loadingMessage = await message.reply('⏳ **Loading and deploying commands...**');
    
        try {
            const commands = [];
            const foldersPath = join(import.meta.dirname, '../../commands');
            const commandFolders = await readdir(foldersPath, { withFileTypes: true });
            
            for (const folder of commandFolders) {
                if (!folder.isDirectory()) continue;
                
                const commandsPath = join(foldersPath, folder.name);
                const commandFiles = (await readdir(commandsPath)).filter(file => file.endsWith('.js'));
                
                for (const file of commandFiles) {
                    const filePath = join(commandsPath, file);
                    const fileUrl = pathToFileURL(filePath).href;
                    const { default: command } = await import(fileUrl);
                    
                    if (command && 'data' in command && 'execute' in command) {
                        commands.push(command.data.toJSON());
                    } else {
                        console.log(`[WARNING] The command at ${file} is missing required properties.`);
                    }
                }
            }
            const rest = new REST().setToken(process.env.TOKEN);
            const data = await rest.put(
                Routes.applicationCommands(process.env.BOT_ID),
                { body: commands },
            );
            
            await loadingMessage.edit(`✅ **Success!** Deployed \`${data.length}\` application (/) commands.`);
        } catch (error) {
            console.error('[Deploy Error]:', error);
            await loadingMessage.edit('❌ **Error deploying commands. Check console.**');
        }
    }
    
export default {
    name: 'deploy', execute,
};