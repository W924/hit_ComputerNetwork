/*
* THIS FILE IS FOR IP TEST
*/
// system support
#include "sysInclude.h"

extern void ip_DiscardPkt(char* pBuffer,int type);

extern void ip_SendtoLower(char*pBuffer,int length);

extern void ip_SendtoUp(char *pBuffer,int length);

extern unsigned int getIpv4Address();

// implemented by students

struct Ipv4{
	char version_headlen;		// 版本号与首部长度
	char TOS;				  	// 服务类型
	short total_len;		 	// 报文总长度
	short identification;		// 标识
	short flag_offset;			// 标志位以及片偏移
	char TTL;					// 生存时间
	char protocol;				// 上层协议类型
	short header_checksum;		// 首部校验和
	unsigned int source_addr;	// 源IP地址
	unsigned int dest_addr;		// 目的IP地址
	
	Ipv4() {memset(this,0,sizeof(Ipv4));}
};

short compute_checksum(char *pBuffer, int header_len) {
	int i, sum = 0;
	for(i = 0; i < header_len * 2; i++) {
		if(i != 5)
		{
			sum += (int)((unsigned char)pBuffer[i * 2] << 8);
			sum += (int)((unsigned char)pBuffer[i * 2 + 1]);
		}
	}
	while((sum & 0xffff0000) != 0) {
		sum = (sum & 0xffff) + ((sum >> 16) & 0xffff);
	}
	return (~sum) & 0xffff;
}

int stud_ip_recv(char *pBuffer,unsigned short length) {
	Ipv4 *ipv4 = new Ipv4();
	*ipv4 = *(Ipv4*)pBuffer;
	
	int version = 0xf0 & ipv4->version_headlen;
	int header_len = 0xf & ipv4->version_headlen;
	int ttl = (int)ipv4->TTL;
	int dest_addr = ntohl(ipv4->dest_addr);  
	int local_addr = getIpv4Address();
	short header_checksum = ntohs(ipv4->header_checksum);
	short checksum_cal = compute_checksum(pBuffer, header_len);
	
	if(version != 0x40)  {
	ip_DiscardPkt(pBuffer, STUD_IP_TEST_VERSION_ERROR);
		return 1;
	}

	if(header_len < 0x05) {
	ip_DiscardPkt(pBuffer, STUD_IP_TEST_HEADLEN_ERROR);
		return 1;
	}

	if(ttl <= 0) {
		ip_DiscardPkt(pBuffer, STUD_IP_TEST_TTL_ERROR);
		return 1;
	}
	
	if(checksum_cal != header_checksum) {
		ip_DiscardPkt(pBuffer, STUD_IP_TEST_CHECKSUM_ERROR);
		return 1;
	}
	
	if(dest_addr != local_addr && dest_addr != 0xffffffff) {
		ip_DiscardPkt(pBuffer, STUD_IP_TEST_DESTINATION_ERROR);
		return 1;
	}
	
	ip_SendtoUp(pBuffer,length);
	return 0;
}

int stud_ip_Upsend(char *pBuffer, unsigned short len, unsigned int srcAddr, 
					unsigned int dstAddr, byte protocol, byte ttl) {
	
	byte *pkt_send = new byte[len + 20];
	memset(pkt_send, 0, len+20);
	
	pkt_send[0] = 0x45;
	pkt_send[1] = 0x80; 
	pkt_send[8] = ttl;
	pkt_send[9] = protocol;
	
	*(short *)(pkt_send + 2) = htons(20 + len);
	*(int *)(pkt_send + 12) = ntohl(srcAddr);
	*(int *)(pkt_send + 16) = ntohl(dstAddr);
	*(short *)(pkt_send + 10) = htons(compute_checksum(pkt_send, 5));
	
	memcpy(pkt_send + 20, pBuffer, len);
	
	ip_SendtoLower(pkt_send, len + 20);
	return 0;
}
