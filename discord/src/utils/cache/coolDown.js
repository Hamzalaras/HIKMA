import redisClient from './redisClient.js';

export const CoolDownManager = {
    async check({ userId, commandName, coolDownSeconds = 3 }) {
        const redisKey = `coolDown:${commandName}:${userId}`;
        
        const result = await redisClient.set(redisKey, 'active', 'EX', coolDownSeconds, 'NX');

        if (!result) {
            const ttl = await redisClient.ttl(redisKey);
            return { isLimited: true, timeLeft: ttl };
        }

        return { isLimited: false, timeLeft: 0 };
    }
};