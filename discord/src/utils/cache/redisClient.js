import Redis from 'ioredis';

const redisClient = new Redis(process.env.REDIS_URL || 'redis://127.0.0.1:6379', {
    maxRetriesPerRequest: 1,
    connectTimeout: 500,
    reconnectOnError: (err) => {
        const targetError = 'READONLY';
        if (err.message.includes(targetError)) return true;
        return false;
    }
});

redisClient.on('connect', () => {
    console.log('[Redis]: Connected successfully.');
});

redisClient.on('error', (err) => {
    // console.error('[Redis Error]:', err.message);
});

export default redisClient;