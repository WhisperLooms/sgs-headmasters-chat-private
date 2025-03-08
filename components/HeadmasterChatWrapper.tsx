import dynamic from 'next/dynamic';

const HeadmasterChat = dynamic(() => import('./HeadmasterChat'), { ssr: false });

export default HeadmasterChat;
