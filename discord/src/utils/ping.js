import express from 'express';


export const ping = () => {
    const app = express();
    const PORT = process.env.PORT || 3000;
    
    app.get('/', (req, res) => {
        res.send('working !!!');
    });
    
    app.listen(PORT, () => {
        console.log(`keep alive Server is listening on port ${PORT}`);
    });
};