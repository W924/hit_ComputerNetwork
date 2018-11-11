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

short compute_checksum(char *pBuffer, int header_len) {
	int i, sum = 0;
	for(i = 0; i < header_len * 2; i++) {
		if(i != 5)
		{
			sum += (int)((unsigned char)pBuffer[i*2] << 8);
			sum += (int)((unsigned char)pBuffer[i*2+1]);
		}
	}

	while((sum & 0xffff0000) != 0) {
		sum = (sum & 0xffff) + ((sum >> 16) & 0xffff);
	}
	return (~sum) & 0xffff;
}

struct Ipv4{
	char version_headlen;
	char TOS;
	short total_len;
	short identification;
	short flag_offset;
	char TTL;
	char protocol;
	short header_checksum;
	unsigned int source_addr;
	unsigned int dest_addr;
	
	Ipv4() {memset(this,0,sizeof(Ipv4));}
	Ipv4(unsigned int len,unsigned int srcAddr,unsigned int dstAddr, byte _protocol,byte ttl) {
		memset(this,0,sizeof(Ipv4));
		version_headlen = 0x45;
		total_len = htons(len+20);
		TTL = ttl;
		protocol = _protocol;
		source_addr = htonl(srcAddr);
		dest_addr = htonl(dstAddr);
    
		char *pBuffer;
		memcpy(pBuffer,this,sizeof(Ipv4));
		header_checksum = htons(compute_checksum(pBuffer, 5));
	}
	
};

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
	ip_DiscardPkt(pBuffer,STUD_IP_TEST_VERSION_ERROR);
		return 1;
	}

	if(header_len < 0x05) {
	ip_DiscardPkt(pBuffer,STUD_IP_TEST_HEADLEN_ERROR);
		return 1;
	}

	if(ttl == 0) {
		ip_DiscardPkt(pBuffer,STUD_IP_TEST_TTL_ERROR);
		return 1;
	}
	
	if(checksum_cal != header_checksum) {
		ip_DiscardPkt(pBuffer,STUD_IP_TEST_CHECKSUM_ERROR);
		return 1;
	}
	
	if(dest_addr != local_addr && dest_addr != 0xffffffff) {
		ip_DiscardPkt(pBuffer,STUD_IP_TEST_DESTINATION_ERROR);
		return 1;
	}
	
	ip_SendtoUp(pBuffer,length);
	return 0;
}

int stud_ip_Upsend(char *pBuffer, unsigned short len, unsigned int srcAddr, unsigned int dstAddr, byte protocol, byte ttl) {
	
	char *pkt_send = new char[len+20];
	memset(pkt_send,0,len+20);
	*((Ipv4*)pkt_send) = Ipv4(len,srcAddr,dstAddr,protocol,ttl);
	memcpy(pkt_send+20,pBuffer,len);
	
	ip_SendtoLower(pkt_send,len+20);
	return 0;
}
